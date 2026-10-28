/**
 * Quality gate implementations for ingestion pipeline.
 * Matches CONTRACT.md §2.2 qualityGates and §2.4 validation contract.
 */

import { QualityGateResult, ErrorDetail, ArtifactRef, TechnicalMetadata } from '../types';
import * as fs from 'fs';
import * as path from 'path';
import ffmpeg from 'fluent-ffmpeg';
import ffmpegStatic from 'ffmpeg-static';

ffmpeg.setFfmpegPath(ffmpegStatic || 'ffmpeg');

export interface GateContext {
  artifact: ArtifactRef;
  metadata?: TechnicalMetadata;
  transcript?: { segments: Array<{ text: string }>; vtt: string };
}

export async function gateFileExists(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const { artifact } = context;

  try {
    const filePath = artifact.location.replace('file://', '');
    await fs.promises.access(filePath, fs.constants.R_OK);
  } catch {
    errors.push({
      code: 'FILE_NOT_FOUND',
      message: `Source file not found or not readable: ${artifact.location}`,
      severity: 'error'
    });
  }

  return {
    gateId: 'gate-file-exists',
    passed: errors.length === 0,
    errors,
    warnings: []
  };
}

export async function gateVideoCodec(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const warnings: ErrorDetail[] = [];
  const { metadata } = context;

  if (!metadata) {
    errors.push({
      code: 'NO_METADATA',
      message: 'Technical metadata required for codec validation',
      severity: 'error'
    });
    return { gateId: 'gate-video-codec', passed: false, errors, warnings };
  }

  const videoStream = metadata.streams.find((s: { codecType: string }) => s.codecType === 'video');
  if (!videoStream) {
    errors.push({
      code: 'NO_VIDEO_STREAM',
      message: 'No video stream found in source footage',
      severity: 'error'
    });
    return { gateId: 'gate-video-codec', passed: false, errors, warnings };
  }

  const allowedCodecs = ['h264', 'hevc', 'prores', 'prores_ks', 'prores_hq', 'prores_422', 'prores_4444'];
  const codec = videoStream.codecName.toLowerCase();

  if (!allowedCodecs.some(c => codec.includes(c))) {
    errors.push({
      code: 'UNSUPPORTED_CODEC',
      message: `Unsupported video codec: ${videoStream.codecName}. Allowed: h264, hevc, prores`,
      severity: 'error'
    });
  }

  return {
    gateId: 'gate-video-codec',
    passed: errors.length === 0,
    errors,
    warnings
  };
}

export async function gateDuration(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const warnings: ErrorDetail[] = [];
  const { metadata } = context;

  if (!metadata) {
    errors.push({
      code: 'NO_METADATA',
      message: 'Technical metadata required for duration validation',
      severity: 'error'
    });
    return { gateId: 'gate-duration', passed: false, errors, warnings };
  }

  const duration = metadata.format.duration;
  if (!duration || duration <= 0) {
    errors.push({
      code: 'INVALID_DURATION',
      message: 'Duration must be greater than 0',
      severity: 'error'
    });
  } else if (duration > 86400) {
    errors.push({
      code: 'DURATION_TOO_LONG',
      message: 'Duration exceeds 24 hours maximum',
      severity: 'error'
    });
  } else if (duration < 1) {
    warnings.push({
      code: 'SHORT_DURATION',
      message: 'Duration is less than 1 second',
      severity: 'warning'
    });
  }

  return {
    gateId: 'gate-duration',
    passed: errors.length === 0,
    errors,
    warnings
  };
}

export async function gateMetadataComplete(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const warnings: ErrorDetail[] = [];
  const { metadata } = context;

  if (!metadata) {
    errors.push({
      code: 'NO_METADATA',
      message: 'Technical metadata artifact is missing',
      severity: 'error'
    });
    return { gateId: 'gate-metadata-complete', passed: false, errors, warnings };
  }

  const requiredFields = ['format', 'streams'];
  for (const field of requiredFields) {
    if (!metadata[field as keyof TechnicalMetadata]) {
      errors.push({
        code: 'MISSING_METADATA_FIELD',
        message: `Required metadata field missing: ${field}`,
        severity: 'error'
      });
    }
  }

  const videoStream = metadata.streams.find((s: { codecType: string; width?: number; height?: number; codecName?: string; frameRate?: string }) => s.codecType === 'video');
  if (videoStream) {
    const requiredVideoFields = ['width', 'height', 'codecName', 'frameRate'];
    for (const field of requiredVideoFields) {
      if (!videoStream[field as keyof typeof videoStream]) {
        warnings.push({
          code: 'MISSING_VIDEO_FIELD',
          message: `Video stream missing optional field: ${field}`,
          severity: 'warning'
        });
      }
    }
  }

  const audioStream = metadata.streams.find((s: { codecType: string; sampleRate?: number; channels?: number; codecName?: string }) => s.codecType === 'audio');
  if (audioStream) {
    const requiredAudioFields = ['sampleRate', 'channels', 'codecName'];
    for (const field of requiredAudioFields) {
      if (!audioStream[field as keyof typeof audioStream]) {
        warnings.push({
          code: 'MISSING_AUDIO_FIELD',
          message: `Audio stream missing optional field: ${field}`,
          severity: 'warning'
        });
      }
    }
  }

  return {
    gateId: 'gate-metadata-complete',
    passed: errors.length === 0,
    errors,
    warnings
  };
}

export async function gateTranscriptValid(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const warnings: ErrorDetail[] = [];
  const { transcript } = context;

  if (!transcript) {
    errors.push({
      code: 'NO_TRANSCRIPT',
      message: 'Transcript artifact is missing',
      severity: 'error'
    });
    return { gateId: 'gate-transcript-valid', passed: false, errors, warnings };
  }

  if (!transcript.segments || transcript.segments.length === 0) {
    errors.push({
      code: 'EMPTY_TRANSCRIPT',
      message: 'Transcript contains no segments',
      severity: 'error'
    });
  }

  const hasText = transcript.segments.some(s => s.text && s.text.trim().length > 0);
  if (!hasText) {
    warnings.push({
      code: 'TRANSCRIPT_NO_TEXT',
      message: 'Transcript segments contain no readable text',
      severity: 'warning'
    });
  }

  if (!transcript.vtt || transcript.vtt.trim().length === 0) {
    warnings.push({
      code: 'MISSING_VTT',
      message: 'VTT format output is empty',
      severity: 'warning'
    });
  }

  return {
    gateId: 'gate-transcript-valid',
    passed: errors.length === 0,
    errors,
    warnings
  };
}

export async function gateProxyPlayable(context: GateContext): Promise<QualityGateResult> {
  const errors: ErrorDetail[] = [];
  const warnings: ErrorDetail[] = [];
  const { artifact, metadata } = context;

  if (!artifact.location || artifact.location.trim() === '') {
    errors.push({
      code: 'NO_PROXY_LOCATION',
      message: 'Proxy artifact has no location',
      severity: 'error'
    });
    return { gateId: 'gate-proxy-playable', passed: false, errors, warnings };
  }

  try {
    const filePath = artifact.location.replace('file://', '');
    await fs.promises.access(filePath, fs.constants.R_OK);
  } catch {
    errors.push({
      code: 'PROXY_NOT_FOUND',
      message: `Proxy file not found: ${artifact.location}`,
      severity: 'error'
    });
    return { gateId: 'gate-proxy-playable', passed: false, errors, warnings };
  }

  if (metadata) {
    const proxyVideoStream = metadata.streams.find((s: { codecType: string; duration?: number }) => s.codecType === 'video');
    const sourceVideoStream = metadata.streams.find((s: { codecType: string; duration?: number }) => s.codecType === 'video');

    if (proxyVideoStream && sourceVideoStream && proxyVideoStream.duration && sourceVideoStream.duration) {
      const durationDiff = Math.abs(proxyVideoStream.duration - sourceVideoStream.duration);
      const tolerance = sourceVideoStream.duration * 0.01;

      if (durationDiff > tolerance) {
        warnings.push({
          code: 'DURATION_MISMATCH',
          message: `Proxy duration differs from source by ${durationDiff.toFixed(2)}s (tolerance: ${tolerance.toFixed(2)}s)`,
          severity: 'warning'
        });
      }
    }
  }

  return {
    gateId: 'gate-proxy-playable',
    passed: errors.length === 0,
    errors,
    warnings
  };
}

export const allGates = [
  gateFileExists,
  gateVideoCodec,
  gateDuration,
  gateMetadataComplete,
  gateTranscriptValid,
  gateProxyPlayable
];

export async function runGates(
  gateIds: string[],
  context: GateContext
): Promise<QualityGateResult[]> {
  const gateMap: Record<string, (ctx: GateContext) => Promise<QualityGateResult>> = {
    'gate-file-exists': gateFileExists,
    'gate-video-codec': gateVideoCodec,
    'gate-duration': gateDuration,
    'gate-metadata-complete': gateMetadataComplete,
    'gate-transcript-valid': gateTranscriptValid,
    'gate-proxy-playable': gateProxyPlayable
  };

  const results: QualityGateResult[] = [];
  for (const gateId of gateIds) {
    const gateFn = gateMap[gateId];
    if (gateFn) {
      results.push(await gateFn(context));
    } else {
      results.push({
        gateId,
        passed: false,
        errors: [{
          code: 'UNKNOWN_GATE',
          message: `Unknown quality gate: ${gateId}`,
          severity: 'error'
        }],
        warnings: []
      });
    }
  }
  return results;
}