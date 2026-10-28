/**
 * Core type definitions for Asset Manager ingestion flow.
 * Matches CONTRACT.md §2.1-2.4 and §3 asset_manifest schema.
 */

export type ArtifactType = 'video' | 'transcript' | 'metadata' | 'proxy' | 'thumbnail';
export type ValidationStatus = 'pending' | 'valid' | 'invalid' | 'deferred';
export type AgentRole = 'ingestion' | 'transcription' | 'translation' | 'editing' | 'qc' | 'delivery';
export type StageStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
export type ValidationResultStatus = 'pass' | 'fail';

export interface ArtifactRef {
  artifactType: ArtifactType;
  artifactId: string; // UUID v4
  version: string;    // semver MAJOR.MINOR.PATCH
  location: string;   // URI (file://, s3://, https://)
  producerStage: string; // stageId that produced this
  validationStatus: ValidationStatus;
}

export interface GateDef {
  gateId: string;
  criteria: string;
  validationScript: string;
}

export interface Stage {
  stageId: string;           // UUID v4
  agentRole: AgentRole;
  dependsOn: string[];       // array of stageId
  inputs: ArtifactRef[];
  outputs: ArtifactRef[];
  qualityGates: GateDef[];
  status: StageStatus;
  startedAt?: string;        // ISO8601
  completedAt?: string;      // ISO8601
}

export interface DecisionLog {
  timestamp: string;         // ISO8601
  stageId: string;
  decision: string;
  rationale: string;
  relatedArtifacts?: ArtifactRef[];
}

export interface ValidationReport {
  artifactReference: ArtifactRef;
  timestamp: string;         // ISO8601
  status: ValidationResultStatus;
  errors: ErrorDetail[];
  warnings: WarningDetail[];
}

export interface ErrorDetail {
  code: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface WarningDetail {
  code: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationSummary {
  totalGates: number;
  passed: number;
  failed: number;
  deferred: number;
}

export interface AssetManifest {
  manifestId: string;           // UUID v4
  manifestVersion: string;      // semver of schema (e.g., "2.0.0")
  createdAt: string;            // ISO8601
  updatedAt: string;            // ISO8601
  sourceFootage: ArtifactRef;
  stages: Stage[];
  artifacts: ArtifactRef[];
  decisionLog: DecisionLog[];
  validationSummary: ValidationSummary;
  description?: string;
  tags?: string[];
  license?: string;
  metadata?: Record<string, unknown>;
}

export interface IngestionConfig {
  inputPath: string;
  outputDir: string;
  manifestPath?: string;
  storageBaseUri?: string; // e.g., s3://bucket/path or file:///path
  enableTranscript?: boolean;
  whisperModel?: string;
}

export interface IngestionResult {
  manifest: AssetManifest;
  artifacts: ArtifactRef[];
}

export interface QualityGateResult {
  gateId: string;
  passed: boolean;
  errors: ErrorDetail[];
  warnings: WarningDetail[];
}

export interface MetadataExtractionResult {
  artifact: ArtifactRef;
  metadata: TechnicalMetadata;
  gateResults: QualityGateResult[];
  stage?: Stage;
}

export interface TranscriptGenerationResult {
  artifact: ArtifactRef;
  transcript: TranscriptData;
  gateResults: QualityGateResult[];
  stage?: Stage;
}

export interface TechnicalMetadata {
  format: {
    formatName: string;
    formatLongName: string;
    duration: number;
    size: number;
    bitRate: number;
    probeScore: number;
  };
  streams: Array<{
    index: number;
    codecType: 'video' | 'audio' | 'subtitle' | 'data';
    codecName: string;
    codecLongName: string;
    profile?: string;
    width?: number;
    height?: number;
    codedWidth?: number;
    codedHeight?: number;
    displayAspectRatio?: string;
    sampleAspectRatio?: string;
    frameRate?: string;
    avgFrameRate?: string;
    timeBase?: string;
    startTime?: number;
    duration?: number;
    bitRate?: number;
    sampleRate?: number;
    channels?: number;
    channelLayout?: string;
    bitsPerSample?: number;
    tags?: Record<string, string>;
  }>;
}

export interface TranscriptData {
  language: string;
  duration: number;
  segments: Array<{
    id: number;
    start: number;
    end: number;
    text: string;
    confidence?: number;
  }>;
  vtt: string;
}

export function createArtifactRef(
  artifactType: ArtifactType,
  location: string,
  producerStage: string,
  version: string = '1.0.0'
): ArtifactRef {
  return {
    artifactType,
    artifactId: crypto.randomUUID(),
    version,
    location,
    producerStage,
    validationStatus: 'pending'
  };
}

export function createStage(
  agentRole: AgentRole,
  dependsOn: string[],
  inputs: ArtifactRef[],
  qualityGates: GateDef[]
): Stage {
  return {
    stageId: crypto.randomUUID(),
    agentRole,
    dependsOn,
    inputs,
    outputs: [],
    qualityGates,
    status: 'pending'
  };
}

export function createInitialManifest(
  sourceFootage: ArtifactRef,
  stage: Stage
): AssetManifest {
  const now = new Date().toISOString();
  return {
    manifestId: crypto.randomUUID(),
    manifestVersion: '2.0.0',
    createdAt: now,
    updatedAt: now,
    sourceFootage,
    stages: [stage],
    artifacts: [sourceFootage],
    decisionLog: [],
    validationSummary: {
      totalGates: stage.qualityGates.length,
      passed: 0,
      failed: 0,
      deferred: 0
    }
  };
}

export function appendStageToManifest(
  manifest: AssetManifest,
  stage: Stage,
  decision: DecisionLog
): AssetManifest {
  const now = new Date().toISOString();
  const newManifest = { ...manifest };
  newManifest.stages = [...manifest.stages, stage];
  newManifest.artifacts = [...manifest.artifacts, ...stage.outputs];
  newManifest.decisionLog = [...manifest.decisionLog, decision];
  newManifest.updatedAt = now;

  const newGates = stage.qualityGates.length;
  newManifest.validationSummary.totalGates += newGates;

  return newManifest;
}

export function validateManifestDeduplication(manifest: AssetManifest): string[] {
  const errors: string[] = [];
  const artifactMap = new Map<string, ArtifactRef>();

  for (const artifact of manifest.artifacts) {
    const key = `${artifact.artifactId}@${artifact.version}`;
    if (artifactMap.has(key)) {
      errors.push(`Duplicate artifact in artifacts[]: ${key}`);
    } else {
      artifactMap.set(key, artifact);
    }
  }

  const checkRefs = (refs: ArtifactRef[], context: string) => {
    for (const ref of refs) {
      const key = `${ref.artifactId}@${ref.version}`;
      if (!artifactMap.has(key)) {
        errors.push(`${context}: artifact reference not found in artifacts[]: ${key}`);
      }
    }
  };

  checkRefs([manifest.sourceFootage], 'sourceFootage');
  for (const stage of manifest.stages) {
    checkRefs(stage.inputs, `stage ${stage.stageId} inputs`);
    checkRefs(stage.outputs, `stage ${stage.stageId} outputs`);
  }
  for (const decision of manifest.decisionLog) {
    if (decision.relatedArtifacts) {
      checkRefs(decision.relatedArtifacts, `decisionLog ${decision.timestamp}`);
    }
  }

  return errors;
}