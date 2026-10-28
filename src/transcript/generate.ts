/**
 * Transcript generation using whisper.cpp or compatible tool.
 * Outputs transcript artifact per CONTRACT.md §4.2 enrichment pattern.
 */

import * as fs from 'fs';
import * as path from 'path';
import { spawn } from 'child_process';
import {
  ArtifactRef,
  TranscriptGenerationResult,
  TranscriptData,
  GateDef,
  Stage,
  createArtifactRef,
  createStage
} from '../types';
import { gateTranscriptValid } from '../validation/gates';

export interface TranscriptOptions {
  sourceArtifact: ArtifactRef;
  sourcePath: string;
  outputDir: string;
  storageBaseUri?: string;
  stageDependsOn: string;
  whisperModel?: string;
  language?: string;
}

export async function generateTranscript(
  options: TranscriptOptions
): Promise<TranscriptGenerationResult> {
  const {
    sourceArtifact,
    sourcePath,
    outputDir,
    storageBaseUri = `file://${outputDir}`,
    stageDependsOn,
    whisperModel = 'base',
    language = 'auto'
  } = options;

  const absOutputDir = path.resolve(outputDir);
  await fs.promises.mkdir(absOutputDir, { recursive: true });

  const transcriptData = await runWhisper(sourcePath, whisperModel, language);

  const baseName = path.basename(sourcePath, path.extname(sourcePath));
  const transcriptJsonFile = `${baseName}-transcript.json`;
  const transcriptVttFile = `${baseName}-transcript.vtt`;

  const jsonPath = path.join(absOutputDir, transcriptJsonFile);
  const vttPath = path.join(absOutputDir, transcriptVttFile);

  const jsonUri = `${storageBaseUri.replace(/\/$/, '')}/${transcriptJsonFile}`;
  const vttUri = `${storageBaseUri.replace(/\/$/, '')}/${transcriptVttFile}`;

  await fs.promises.writeFile(jsonPath, JSON.stringify(transcriptData, null, 2), 'utf-8');
  await fs.promises.writeFile(vttPath, transcriptData.vtt, 'utf-8');

  const transcriptArtifact = createArtifactRef(
    'transcript',
    jsonUri,
    '',
    '1.0.0'
  );

  const qualityGates: GateDef[] = [
    { gateId: 'gate-transcript-valid', criteria: 'Transcript is non-empty and properly formatted', validationScript: 'gates.ts::gateTranscriptValid' }
  ];

  const stage = createStage('transcription', [stageDependsOn], [sourceArtifact], qualityGates);
  transcriptArtifact.producerStage = stage.stageId;

  const gateContext = {
    artifact: transcriptArtifact,
    transcript: transcriptData
  };

  const gateResults = await gateTranscriptValid(gateContext);

  if (gateResults.passed) {
    transcriptArtifact.validationStatus = 'valid';
  } else {
    transcriptArtifact.validationStatus = 'invalid';
  }

  stage.outputs = [transcriptArtifact];
  stage.status = 'completed';
  stage.startedAt = new Date().toISOString();
  stage.completedAt = new Date().toISOString();

  return { artifact: transcriptArtifact, transcript: transcriptData, gateResults: [gateResults] };
}

function runWhisper(
  audioPath: string,
  model: string,
  language: string
): Promise<TranscriptData> {
  return new Promise((resolve, reject) => {
    const whisperPath = findWhisperExecutable();
    if (!whisperPath) {
      reject(new Error('whisper.cpp not found. Install whisper.cpp or set WHISPER_PATH env var.'));
      return;
    }

    const args = [
      '-m', getModelPath(model),
      '-f', audioPath,
      '--output-json',
      '--output-vtt',
      '--no-timestamps=false'
    ];

    if (language !== 'auto') {
      args.push('-l', language);
    }

    const proc = spawn(whisperPath, args, {
      cwd: path.dirname(audioPath)
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });

    proc.on('close', async (code) => {
      if (code !== 0) {
        reject(new Error(`whisper.cpp exited with code ${code}: ${stderr}`));
        return;
      }

      try {
        const jsonFile = `${path.basename(audioPath, path.extname(audioPath))}.json`;
        const vttFile = `${path.basename(audioPath, path.extname(audioPath))}.vtt`;

        const jsonPath = path.join(path.dirname(audioPath), jsonFile);
        const vttPath = path.join(path.dirname(audioPath), vttFile);

        const [jsonContent, vttContent] = await Promise.all([
          fs.promises.readFile(jsonPath, 'utf-8').catch(() => '{}'),
          fs.promises.readFile(vttPath, 'utf-8').catch(() => '')
        ]);

        const transcript = parseWhisperOutput(jsonContent, vttContent);
        resolve(transcript);
      } catch (err) {
        reject(err);
      }
    });
  });
}

function findWhisperExecutable(): string | null {
  if (process.env.WHISPER_PATH) {
    return process.env.WHISPER_PATH;
  }
  const commonPaths = [
    '/usr/local/bin/whisper-cli',
    '/opt/homebrew/bin/whisper-cli',
    'whisper-cli',
    'whisper'
  ];
  for (const p of commonPaths) {
    try {
      require('fs').accessSync(p, require('fs').constants.X_OK);
      return p;
    } catch { }
  }
  return null;
}

function getModelPath(model: string): string {
  if (process.env.WHISPER_MODEL_PATH) {
    return path.join(process.env.WHISPER_MODEL_PATH, `ggml-${model}.bin`);
  }
  return path.join(process.cwd(), 'models', `ggml-${model}.bin`);
}

function parseWhisperOutput(jsonContent: string, vttContent: string): TranscriptData {
  let data: any = {};
  try {
    data = JSON.parse(jsonContent);
  } catch {
    data = { language: 'en', segments: [] };
  }

  return {
    language: data.language || 'en',
    duration: data.duration || 0,
    segments: (data.segments || []).map((s: any, i: number) => ({
      id: i,
      start: s.start || 0,
      end: s.end || 0,
      text: s.text || '',
      confidence: s.confidence
    })),
    vtt: vttContent
  };
}

export async function runGenerateTranscriptCLI(args: string[]): Promise<void> {
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

    const result = await generateTranscript({
      sourceArtifact,
      sourcePath: config.sourcePath,
      outputDir: config.outputDir,
      storageBaseUri: config.storageBaseUri,
      stageDependsOn: config.stageDependsOn,
      whisperModel: config.whisperModel,
      language: config.language
    });

    console.log('✓ Transcript generation successful');
    console.log(`  Artifact: ${result.artifact.artifactId}`);
    console.log(`  Location: ${result.artifact.location}`);
    console.log(`  Validation: ${result.artifact.validationStatus}`);
    console.log(`  Segments: ${result.transcript.segments.length}`);
  } catch (error) {
    console.error('✗ Transcript generation failed:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

function parseCLIArgs(args: string[]): {
  sourcePath: string;
  outputDir: string;
  sourceArtifactId: string;
  stageDependsOn: string;
  storageBaseUri?: string;
  whisperModel?: string;
  language?: string;
} {
  const config: any = {
    outputDir: './output',
    storageBaseUri: 'file://./output',
    whisperModel: 'base',
    language: 'auto'
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
      case '--model':
        config.whisperModel = args[++i];
        break;
      case '--language':
        config.language = args[++i];
        break;
    }
  }

  if (!config.sourcePath || !config.sourceArtifactId || !config.stageDependsOn) {
    throw new Error('--source, --source-artifact-id, and --stage-depends-on are required');
  }

  return config;
}

if (require.main === module) {
  runGenerateTranscriptCLI(process.argv.slice(2)).catch(console.error);
}