/**
 * Asset manifest builder - composes initial manifest and appends enrichment stages.
 * Implements CONTRACT.md §4.1 and §4.2 patterns.
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  AssetManifest,
  ArtifactRef,
  Stage,
  DecisionLog,
  IngestionResult,
  MetadataExtractionResult,
  TranscriptGenerationResult,
  appendStageToManifest,
  validateManifestDeduplication
} from '../types';

export { validateManifestDeduplication } from '../types';

export interface ManifestBuilderOptions {
  initialResult: IngestionResult;
  metadataResult?: MetadataExtractionResult;
  transcriptResult?: TranscriptGenerationResult;
  manifestPath?: string;
}

export function buildManifest(options: ManifestBuilderOptions): AssetManifest {
  let manifest = options.initialResult.manifest;

  if (options.metadataResult) {
    const decision: DecisionLog = {
      timestamp: new Date().toISOString(),
      stageId: options.metadataResult.artifact.producerStage,
      decision: 'Extracted technical metadata using FFmpeg probe',
      rationale: 'FFmpeg provides comprehensive codec/format metadata reliably',
      relatedArtifacts: [
        manifest.sourceFootage,
        options.metadataResult.artifact
      ]
    };
    const ingestStageId = manifest.stages[0].stageId;
    manifest = appendStageToManifest(manifest, createEnrichmentStage(options.metadataResult, ingestStageId, manifest.sourceFootage), decision);
  }

  if (options.transcriptResult) {
    const decision: DecisionLog = {
      timestamp: new Date().toISOString(),
      stageId: options.transcriptResult.artifact.producerStage,
      decision: 'Generated transcript using whisper.cpp',
      rationale: 'Whisper provides accurate speech-to-text for multiple languages',
      relatedArtifacts: [
        manifest.sourceFootage,
        options.transcriptResult.artifact
      ]
    };
    const ingestStageId = manifest.stages[0].stageId;
    manifest = appendStageToManifest(manifest, createEnrichmentStage(options.transcriptResult, ingestStageId, manifest.sourceFootage), decision);
  }

  const dedupErrors = validateManifestDeduplication(manifest);
  if (dedupErrors.length > 0) {
    throw new Error(`Manifest deduplication validation failed: ${dedupErrors.join('; ')}`);
  }

  if (options.manifestPath) {
    writeManifestSync(manifest, options.manifestPath);
  }

  return manifest;
}

function createEnrichmentStage(
  result: MetadataExtractionResult | TranscriptGenerationResult,
  ingestStageId: string,
  sourceArtifact: ArtifactRef
): Stage {
  // Use the stage from the result if provided, otherwise create a new one
  if (result.stage) {
    return result.stage;
  }
  
  const stage: Stage = {
    stageId: result.artifact.producerStage,
    agentRole: result.artifact.artifactType === 'metadata' ? 'ingestion' : 'transcription',
    dependsOn: [ingestStageId],
    inputs: [sourceArtifact],
    outputs: [result.artifact],
    qualityGates: [],
    status: 'completed',
    startedAt: new Date().toISOString(),
    completedAt: new Date().toISOString()
  };
  return stage;
}

function writeManifestSync(manifest: AssetManifest, manifestPath: string): void {
  const dir = path.dirname(manifestPath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
}

export async function writeManifest(manifest: AssetManifest, manifestPath: string): Promise<void> {
  const dir = path.dirname(manifestPath);
  await fs.promises.mkdir(dir, { recursive: true });
  await fs.promises.writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');
}

export function loadManifest(manifestPath: string): AssetManifest {
  const content = fs.readFileSync(manifestPath, 'utf-8');
  return JSON.parse(content) as AssetManifest;
}

export async function loadManifestAsync(manifestPath: string): Promise<AssetManifest> {
  const content = await fs.promises.readFile(manifestPath, 'utf-8');
  return JSON.parse(content) as AssetManifest;
}

export function createIngestionManifest(
  sourceArtifact: ArtifactRef,
  ingestStage: Stage
): AssetManifest {
  const now = new Date().toISOString();
  return {
    manifestId: crypto.randomUUID(),
    manifestVersion: '2.0.0',
    createdAt: now,
    updatedAt: now,
    sourceFootage: sourceArtifact,
    stages: [ingestStage],
    artifacts: [sourceArtifact],
    decisionLog: [],
    validationSummary: {
      totalGates: ingestStage.qualityGates.length,
      passed: ingestStage.qualityGates.filter(() => true).length,
      failed: 0,
      deferred: 0
    }
  };
}

export function validateManifest(manifest: AssetManifest): { valid: boolean; errors: string[] } {
  const dedupErrors = validateManifestDeduplication(manifest);

  const schemaErrors: string[] = [];

  if (!manifest.manifestId) schemaErrors.push('Missing manifestId');
  if (!manifest.manifestVersion) schemaErrors.push('Missing manifestVersion');
  if (!manifest.createdAt) schemaErrors.push('Missing createdAt');
  if (!manifest.updatedAt) schemaErrors.push('Missing updatedAt');
  if (!manifest.sourceFootage) schemaErrors.push('Missing sourceFootage');
  if (!manifest.stages || manifest.stages.length === 0) schemaErrors.push('Missing stages');
  if (!manifest.artifacts || manifest.artifacts.length === 0) schemaErrors.push('Missing artifacts');
  if (!manifest.decisionLog) schemaErrors.push('Missing decisionLog');
  if (!manifest.validationSummary) schemaErrors.push('Missing validationSummary');

  if (manifest.sourceFootage.artifactType !== 'video') {
    schemaErrors.push('sourceFootage must have artifactType=video');
  }

  return {
    valid: dedupErrors.length === 0 && schemaErrors.length === 0,
    errors: [...dedupErrors, ...schemaErrors]
  };
}

export function updateManifestValidationSummary(
  manifest: AssetManifest,
  gateResults: Array<{ gateId: string; passed: boolean }>
): AssetManifest {
  const newManifest = { ...manifest };
  const passed = gateResults.filter(r => r.passed).length;
  const failed = gateResults.filter(r => !r.passed).length;

  newManifest.validationSummary = {
    ...manifest.validationSummary,
    totalGates: manifest.validationSummary.totalGates + gateResults.length,
    passed: manifest.validationSummary.passed + passed,
    failed: manifest.validationSummary.failed + failed
  };
  newManifest.updatedAt = new Date().toISOString();

  return newManifest;
}

if (require.main === module) {
  console.log('Manifest builder module - import and use buildManifest()');
}