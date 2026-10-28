/**
 * Technical metadata extraction using ffprobe.
 * Outputs metadata artifact per CONTRACT.md §4.2 enrichment pattern.
 */

import * as fs from 'fs';
import * as path from 'path';
import ffmpeg from 'fluent-ffmpeg';
import ffmpegStatic from 'ffmpeg-static';
import ffprobeStatic from 'ffprobe-static';
import {
  ArtifactRef,
  MetadataExtractionResult,
  TechnicalMetadata,
  GateDef,
  Stage,
  createArtifactRef,
  createStage
} from '../types';
import { gateMetadataComplete } from '../validation/gates';

ffmpeg.setFfmpegPath(ffmpegStatic || 'ffmpeg');
ffmpeg.setFfprobePath(ffprobeStatic.path || 'ffprobe');

export interface ExtractMetadataOptions {
  sourceArtifact: ArtifactRef;
  sourcePath: string;
  outputDir: string;
  storageBaseUri?: string;
  stageDependsOn: string;
}

export async function extractTechnicalMetadata(
  options: ExtractMetadataOptions
): Promise<MetadataExtractionResult> {
  const {
    sourceArtifact,
    sourcePath,
    outputDir,
    storageBaseUri = `file://${outputDir}`,
    stageDependsOn
  } = options;

  const absOutputDir = path.resolve(outputDir);
  await fs.promises.mkdir(absOutputDir, { recursive: true });

  const metadata = await extractMetadata(sourcePath);

  const metadataFileName = `${path.basename(sourcePath, path.extname(sourcePath))}-tech.json`;
  const metadataPath = path.join(absOutputDir, metadataFileName);
  const metadataUri = `${storageBaseUri.replace(/\/$/, '')}/${metadataFileName}`;

  await fs.promises.writeFile(metadataPath, JSON.stringify(metadata, null, 2), 'utf-8');

  const metadataArtifact = createArtifactRef(
    'metadata',
    metadataUri,
    '', // Will be set after stage creation
    '1.0.0'
  );

  const qualityGates: GateDef[] = [
    { gateId: 'gate-metadata-complete', criteria: 'All required metadata fields extracted', validationScript: 'gates.ts::gateMetadataComplete' }
  ];

  const stage = createStage('ingestion', [stageDependsOn], [sourceArtifact], qualityGates);
  metadataArtifact.producerStage = stage.stageId;

  const gateContext = { artifact: metadataArtifact, metadata };
  const gateResults = await gateMetadataComplete(gateContext);

  const passedGates = gateResults.passed ? 1 : 0;
  const failedGates = gateResults.passed ? 0 : 1;

  if (failedGates > 0) {
    metadataArtifact.validationStatus = 'invalid';
  } else {
    metadataArtifact.validationStatus = 'valid';
  }

  stage.outputs = [metadataArtifact];
  stage.status = 'completed';
  stage.startedAt = new Date().toISOString();
  stage.completedAt = new Date().toISOString();

  return { artifact: metadataArtifact, metadata, gateResults: [gateResults] };
}

function extractMetadata(filePath: string): Promise<TechnicalMetadata> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) {
        reject(err);
      } else {
        resolve(metadata as unknown as TechnicalMetadata);
      }
    });
  });
}

export async function runExtractMetadataCLI(args: string[]): Promise<void> {
  const config = parseCLIArgs(args);
  try {
    const sourceArtifact = {
      artifactType: 'video' as const,
      artifactId: config.sourceArtifactId,
      version: '1.0.0',
      location: config.sourcePath,
      producerStage: config.stageDependsOn,
      validationStatus: 'valid' as const
    };

    const result = await extractTechnicalMetadata({
      sourceArtifact,
      sourcePath: config.sourcePath,
      outputDir: config.outputDir,
      storageBaseUri: config.storageBaseUri,
      stageDependsOn: config.stageDependsOn
    });

    console.log('✓ Metadata extraction successful');
    console.log(`  Artifact: ${result.artifact.artifactId}`);
    console.log(`  Location: ${result.artifact.location}`);
    console.log(`  Validation: ${result.artifact.validationStatus}`);
  } catch (error) {
    console.error('✗ Metadata extraction failed:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

function parseCLIArgs(args: string[]): {
  sourcePath: string;
  outputDir: string;
  sourceArtifactId: string;
  stageDependsOn: string;
  storageBaseUri?: string;
} {
  const config: any = {
    outputDir: './output',
    storageBaseUri: 'file://./output'
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--source':
        config.sourcePath = args[++i];
        break;
      case '--output':
        config.outputDir = args[++i];
        break;
      case '--source-artifact-id':
        config.sourceArtifactId = args[++i];
        break;
      case '--stage-depends-on':
        config.stageDependsOn = args[++i];
        break;
      case '--storage-uri':
        config.storageBaseUri = args[++i];
        break;
    }
  }

  if (!config.sourcePath || !config.sourceArtifactId || !config.stageDependsOn) {
    throw new Error('--source, --source-artifact-id, and --stage-depends-on are required');
  }

  return config;
}

if (require.main === module) {
  runExtractMetadataCLI(process.argv.slice(2)).catch(console.error);
}