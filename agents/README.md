# Ellio Agents

This directory contains the implementation of agents for the Ellio manifest-driven video processing pipeline.

## Agent Types

Each agent is implemented as a standalone Python script that can be executed via command line:
```bash
python agents/<agent-name>/main.py
```

### Core Pipeline Agents
1. **Ingest Agent** (`ingest-agent`) - Video validation and preparation
2. **Transcription Agent** (`transcription-agent`) - Speech-to-text conversion
3. **Translation Agent** (`translation-agent`) - Language translation of transcripts
4. **Subtitle Generation Agent** (`subtitle-generation-agent`) - Creating subtitle files from transcripts

### Extended Pipeline Agents
5. **Audio Agent** (`audio-agent`) - Audio extraction, enhancement, and mixing
6. **Video Effects Agent** (`video-effects-agent`) - Video filters, transitions, and color correction
7. **Metadata Agent** (`metadata-agent`) - Technical metadata extraction using ffprobe
8. **Proxy Agent** (`proxy-agent`) - Low-resolution proxy file generation for editing
9. **Export Agent** (`export-agent`) - Final rendering and export to various formats

## Agent Interface

All agents follow the same interface pattern:

### Inputs
Agents receive input artifact locations via environment variables:
- `INPUT_<ARTIFACT_TYPE>_<INDEX>_PATH` - Path to input artifact
  - Example: `INPUT_VIDEO_0_PATH` for the first video input
  - Example: `INPUT_TRANSCRIPT_0_PATH` for the first transcript input

### Outputs
Agents produce output artifacts at locations specified by:
- `OUTPUT_<ARTIFACT_TYPE>_<INDEX>_PATH` - Path where output artifact should be written
  - Example: `OUTPUT_AUDIO_0_PATH` for the first audio output
  - Example: `OUTPUT_VIDEO_0_PATH` for the first video output

### Parameters
Additional configuration parameters are passed as a JSON string in:
- `AGENT_PARAMETERS` - JSON string of agent-specific parameters

### Execution Contract
- Agents must exit with code 0 for success
- Agents must exit with non-zero code for failure (triggers retry mechanism)
- Agents must produce valid output artifacts matching their declared schema
- Agents should handle missing inputs gracefully and log appropriate errors

## Base Agent

All agents inherit from `BaseAgent` (`agents/base_agent.py`) which provides:
- Common environment variable parsing
- Artifact reference handling
- Logging infrastructure
- Error handling and validation utilities
- Standardized input/output access methods

## Development Guidelines

1. **Inheritance**: All agents must inherit from `BaseAgent`
2. **Naming**: Agent directory name should match the agent class name (in lowercase with hyphens)
3. **Entry Point**: Main execution logic in `main.py`
4. **Dependencies**: Agent-specific Python dependencies in `requirements.txt`
5. **Logging**: Use the provided logger (`self.logger`) for all output
6. **Validation**: Validate inputs and outputs before processing
7. **Atomicity**: Processing should be atomic - either fully succeed or fail cleanly
8. **Idempotency**: Running the same agent multiple times with same inputs should produce same outputs

## Example Workflow

A typical extended video processing pipeline might use these agents in sequence:
1. `ingest-agent` - Validate and prepare source video
2. `metadata-agent` - Extract technical metadata
3. `audio-agent` - Extract and enhance audio tracks
4. `video-effects-agent` - Apply visual effects and color correction
5. `proxy-agent` - Generate editing proxies
6. `transcription-agent` - Convert speech to text
7. `translation-agent` - Translate transcripts to target languages
8. `subtitle-generation-agent` - Create subtitle files from transcripts
9. `export-agent` - Render final output in desired format

Each agent produces artifacts that can be consumed by downstream agents, creating a flexible and extensible processing pipeline.