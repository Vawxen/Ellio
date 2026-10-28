/**
 * Source media ingestion implementation.
 * Accepts source footage, validates, and registers as artifact.
 * Matches CONTRACT.md §4.1 Initial Manifest pattern.
 */

import * as fs from 'fs';
import * as path from 'path';
import { v4 as uuidv4 } from 'uuid';
import ffmpeg from 'fluent-ffmpeg';
import ffmpegStatic from 'ffmpeg-static';
import ffprobeStatic from 'ffprobe-static';
import {
  ArtifactRef,
  IngestionConfig,
  IngestionResult,
  Stage,
  GateDef,
  AssetManifest,
  createArtifactRef,
  createStage,
  createInitialManifest
} from '../types';
import { gateFileExists, gateVideoCodec, gateDuration } from '../validation/gates';

ffmpeg.setFfmpegPath(ffmpegStatic || 'ffmpeg');
ffmpeg.setFfprobePath(ffprobeStatic.path || 'ffprobe');

export interface IngestionOptions extends IngestionConfig {
  sourceFootagePath: string;
  artifactId?: string;
}

export async function ingestSourceFootage(options: IngestionOptions): Promise<IngestionResult> {
  const {
    sourceFootagePath,
    outputDir,
    artifactId,
    storageBaseUri = `file://${outputDir}`,
    manifestPath
  } = options;

  const absInputPath = path.resolve(sourceFootagePath);
  const absOutputDir = path.resolve(outputDir);

  // Check if input file exists before proceeding
  try {
    await fs.promises.access(absInputPath, fs.constants.R_OK);
  } catch {
    throw new Error(`Ingestion validation failed: Source file not found or not readable: ${absInputPath}`);
  }

  await fs.promises.mkdir(absOutputDir, { recursive: true });

  const fileName = path.basename(absInputPath);
  const stagedPath = path.join(absOutputDir, fileName);
  const stagedUri = `${storageBaseUri.replace(/\/$/, '')}/${fileName}`;

  await fs.promises.copyFile(absInputPath, stagedPath);

  const sourceArtifact = createArtifactRef(
    'video',
    stagedUri,
    '', // Will be set after stage creation
    '1.0.0'
  );
  if (artifactId) {
    sourceArtifact.artifactId = artifactId;
  }

  const qualityGates: GateDef[] = [
    { gateId: 'gate-file-exists', criteria: 'File exists and is readable', validationScript: 'gates.ts::gateFileExists' },
    { gateId: 'gate-video-codec', criteria: 'Valid video codec (h264/hevc/prores)', validationScript: 'gates.ts::gateVideoCodec' },
    { gateId: 'gate-duration', criteria: 'Duration > 0 and < 24h', validationScript: 'gates.ts::gateDuration' }
  ];

  const stage = createStage('ingestion', [], [], qualityGates);
  sourceArtifact.producerStage = stage.stageId;

  const metadata = await extractMetadataForValidation(stagedPath);
  const gateContext = { artifact: sourceArtifact, metadata };

  const gateResults = await Promise.all([
    gateFileExists(gateContext),
    gateVideoCodec(gateContext),
    gateDuration(gateContext)
  ]);

  const passedGates = gateResults.filter((g: { passed: boolean }) => g.passed).length;
  const failedGates = gateResults.filter((g: { passed: boolean }) => !g.passed).length;

  if (failedGates > 0) {
    sourceArtifact.validationStatus = 'invalid';
    const allErrors = gateResults.flatMap((g: { errors: Array<{ message: string }> }) => g.errors);
    throw new Error(`Ingestion validation failed: ${allErrors.map((e: { message: string }) => e.message).join('; ')}`);
  }

  sourceArtifact.validationStatus = 'valid';

  stage.outputs = [sourceArtifact];
  stage.status = 'completed';
  stage.startedAt = new Date().toISOString();
  stage.completedAt = new Date().toISOString();

  const manifest = createInitialManifest(sourceArtifact, stage);
  manifest.validationSummary.passed = passedGates;
  manifest.validationSummary.failed = failedGates;

  const decisionLog = {
    timestamp: new Date().toISOString(),
    stageId: stage.stageId,
    decision: 'Accepted source footage; passed initial validation gates',
    rationale: `All ${passedGates} gates passed; footage ready for downstream processing`,
    relatedArtifacts: [sourceArtifact]
  };
  manifest.decisionLog.push(decisionLog);

  if (manifestPath) {
    await writeManifest(manifest, manifestPath);
  }

  return { manifest, artifacts: [sourceArtifact] };
}

async function extractMetadataForValidation(filePath: string): Promise<any> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) {
        resolve(null);
      } else {
        resolve(metadata);
      }
    });
  });
}

async function writeManifest(manifest: AssetManifest, manifestPath: string): Promise<void> {
  const dir = path.dirname(manifestPath);
  await fs.promises.mkdir(dir, { recursive: true });
  await fs.promises.writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
}

export async function runIngestionCLI(args: string[]): Promise<void> {
  const config = parseCLIArgs(args);
  try {
    const result = await ingestSourceFootage(config);
    console.log('✓ Ingestion successful');
    console.log(`  Manifest: ${config.manifestPath || 'not saved'}`);
    console.log(`  Source artifact: ${result.artifacts[0].artifactId}`);
    console.log(`  Location: ${result.artifacts[0].location}`);
  } catch (error) {
    console.error('✗ Ingestion failed:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

function parseCLIArgs(args: string[]): IngestionOptions {
  const config: Partial<IngestionOptions> = {
    outputDir: './output',
    storageBaseUri: 'file://./output'
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input':
        config.sourceFootagePath = args[++i];
        break;
      case '--output':
        config.outputDir = args[++i];
        break;
      case '--manifest':
        config.manifestPath = args[++i];
        break;
      case '--storage-uri':
        config.storageBaseUri = args[++i];
        break;
      case '--artifact-id':
        config.artifactId = args[++i];
        break;
    }
  }

  if (!config.sourceFootagePath) {
    throw new Error('--input is required');
  }

  return config as IngestionOptions;
}

if (require.main === module) {
  runIngestionCLI(process.argv.slice(2)).catch(console.error);
}