# Ellio Pipeline Agents

This directory contains the agent implementations for the Ellio manifest-driven video processing pipeline.

## Agent Overview

| Agent | Stage ID | Input | Output | Description |
|-------|----------|-------|--------|-------------|
| Ingest Agent | `ingest` | `video` (source) | `video` (ingested) | Copies and validates source video |
| Transcription Agent | `transcription` | `video` | `transcript` | Converts speech to text |
| Translation Agent | `translation` | `transcript` | `translated-transcript` | Translates transcript to target language |
| Subtitle Generation Agent | `subtitle-generation` | `translated-transcript` | `subtitles` | Generates SRT subtitle files |

## Agent Interface

All agents follow the same interface contract:

### Environment Variables (set by StageRunner)
- `INPUT_{i}_TYPE` - Artifact type of input i
- `INPUT_{i}_ID` - Artifact ID of input i
- `INPUT_{i}_VERSION` - Version of input i
- `INPUT_{i}_LOCATION` - URI location of input i
- `OUTPUT_{i}_LOCATION` - URI location for output i
- `PARAM_{NAME}` - Workflow parameters (uppercase)
- `STAGE_{KEY}` - Stage configuration values

### Exit Codes
- `0` - Success
- Non-zero - Failure (will trigger retry or workflow failure)

### Output Artifacts
Agents must write output files to the locations specified in `OUTPUT_{i}_LOCATION` environment variables. The orchestration spine will create `ArtifactReference` objects based on the stage definition's outputs array.

## Running Agents Manually

```bash
# Set up environment variables
export INPUT_0_TYPE=video
export INPUT_0_ID=source-video
export INPUT_0_VERSION=1.0.0
export INPUT_0_LOCATION=file:///path/to/input.mp4
export OUTPUT_0_LOCATION=file:///path/to/output.mp4
export STAGE_STAGEID=ingest

# Run agent
python agents/ingest-agent/main.py
```

## Development

### Adding a New Agent
1. Create a new directory under `agents/`
2. Create `main.py` with a class extending `BaseAgent`
3. Implement the `run()` method
4. Add `requirements.txt` if needed
5. Update the manifest to reference the new agent

### Testing
Run the test suite:
```bash
python test_agents.py
```

## Production Considerations

For production deployment, replace mock implementations with actual services:

- **Transcription**: Integrate with `openai-whisper`, `whisper.cpp`, or cloud speech-to-text APIs
- **Translation**: Integrate with `transformers`, Google Translate API, DeepL API, etc.
- **Ingest**: Add video validation, format conversion, proxy generation
- **Subtitle Generation**: Add support for VTT, ASS formats, styling options

## Configuration

Agents can be configured via:
1. Workflow parameters (in manifest `parameters` section)
2. Stage-specific configuration (in stage definition)
3. Environment variables prefixed with `ORCHESTRATION_`

Example manifest parameter:
```json
{
  "parameters": {
    "target_language": "es",
    "whisper_model": "base",
    "output_base_path": "file:///output"
  }
}
```