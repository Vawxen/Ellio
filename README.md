# Manifest-Driven Video Pipeline Orchestration Spine

This is the MVP (Minimum Viable Product) implementation of a manifest-driven orchestration spine for a multi-agent video processing pipeline.

## Features

- **Manifest-Driven Execution**: Workflows defined in JSON manifests
- **Parameter Support**: Manifests can use parameter substitution for reusability
- **Dependency Management**: Automatic dependency resolution and execution ordering
- **Persistent Checkpointing**: Workflow state saved periodically for resumability
- **Resume Capability**: Workflows can be resumed from checkpoints after interruption
- **Structured Handoffs**: Artifact transfers between stages are recorded for auditability
- **Quality Gates**: Schema validation quality gate to ensure artifact correctness
- **Decision Logging**: Comprehensive audit trail of all decisions and events
- **Error Handling**: Retry policies and failure handling

## Architecture

The orchestration spine consists of several key components:

1. **Manifest Parser & Validator** (`src/orchestrator/manifest.py`)
   - Parses and validates JSON manifests
   - Supports parameter substitution
   - Handles manifest versioning

2. **Data Models** (`src/models/`)
   - Immutable artifact references
   - Stage definitions
   - Workflow state tracking
   - Checkpoints, decision logs, handoffs
   - Validation results

3. **Orchestration Engine** (`src/orchestrator/`)
   - Stage runner (command-line execution)
   - Dependency enforcer (topological sorting)
   - Checkpoint manager (persistence)
   - Decision log manager (audit trail)
   - Quality gate engine (schema validation)
   - Handoff recorder (artifact transfers)
   - Workflow executor (main orchestration loop)
   - Resume handler (workflow recovery)

4. **Utilities** (`src/utils/`)
   - Validation helpers
   - Configuration management
   - Storage abstraction (filesystem-based MVP)

## Usage

### Basic Execution

```bash
python -m src.orchestrator.orchestrator manifests/example.json
```

### With Parameters

```bash
python -m src.orchestrator.orchestrator manifests/example_parameterized.json \
  --params '{"suffix": "test123", "workflow_type": "parameterized", "video_path": "file:///tmp/input.mp4"}'
```

### Resume from Checkpoint

```bash
python -m src.orchestrator.orchestrator manifests/example.json --resume
```

### With Custom Configuration

```bash
python -m src.orchestrator.orchestrator manifests/example.json --config my_config.json
```

## Manifest Format

The manifest follows this structure:

```json
{
  "manifestVersion": "1.0.0",
  "workflowId": "unique-workflow-id",
  "name": "Workflow Name",
  "description": "Optional description",
  "stages": [
    {
      "stageId": "stage-id",
      "agentRole": "command-or-script-to-execute",
      "dependsOn": ["dependency-stage-id"],
      "inputs": [
        {
          "artifactType": "video",
          "artifactId": "input-artifact",
          "version": "1.0.0",
          "location": "file:///path/to/input"
        }
      ],
      "outputs": [
        {
          "artifactType": "video",
          "artifactId": "output-artifact",
          "version": "1.0.0",
          "location": "file:///path/to/output"
        }
      ],
      "qualityGates": [
        {
          "gateId": "gate-id",
          "type": "schemaValidation",
          "config": {
            "schemaUri": "schemas/artifact-schema-v1.json"
          }
        }
      ],
      "timeoutSeconds": 300,
      "retryPolicy": {
        "maxAttempts": 3,
        "backoffSeconds": 5
      }
    }
  ],
  "globalQualityGates": [
    {
      "gateId": "global-gate-id",
      "type": "schemaValidation",
      "config": {
        "schemaUri": "schemas/global-artifact-schema-v1.json"
      }
    }
  ]
}
```

## Extending the System

### Adding New Stage Types

Stages are executed as command-line processes by default. The `agentRole` field in the manifest is treated as a command to execute.

To add a new type of stage:
1. Implement the stage as a command-line executable or script
2. Reference it in the manifest using the `agentRole` field
3. Ensure the stage consumes and produces artifacts as specified in its inputs/outputs

### Adding New Quality Gate Types

The quality gate engine is designed to be extensible. To add a new quality gate type:

1. Extend the `QualityGateEngine.validate_artifact()` method to handle your gate type
2. Implement the validation logic for your gate
3. Reference your gate type in the manifest's `qualityGates` array

## Configuration

The system can be configured through:
- Environment variables (prefixed with `ORCHESTRATION_`)
- Configuration files (via `--config` argument)
- Default values in `src/utils/config.py`

Key configuration options:
- Storage paths for checkpoints, handoffs, and decision logs
- Execution timeouts and retry policies
- Checkpointing intervals and retention policies
- Feature flags for advanced capabilities

## Development

### Running Tests

```bash
python -m tests.integration.test_basic_orchestration
```

### Project Structure

```
src/
├── orchestrator/          # Orchestration engine components
│   ├── manifest.py        # Manifest parsing and validation
│   ├── stage_runner.py    # Stage execution
│   ├── dependency_enforcer.py  # Dependency resolution
│   ├── checkpoint_manager.py   # Checkpointing
│   ├── decision_log.py       # Decision logging
│   ├── quality_gate.py       # Quality gate validation
│   ├── handoff_recorder.py   # Handoff recording
│   ├── workflow_executor.py  # Main orchestration logic
│   └── orchestrator.py       # Entry point
├
├── models/                # Data models
│   ├── artifact_reference.py
│   ├── stage_definition.py
│   ├── workflow_state.py
│   ├── parameterized_manifest.py
│   ├── checkpoint.py
│   ├── decision_log_entry.py
│   ├── validation_result.py
│   └── stage_execution_result.py
�└── utils/                 # Utility functions
    ├── validation.py
    ├── config.py
    └── storage.py

manifests/                 # Example manifests
tests/                     # Test files
```

## Requirements

- Python 3.7+
- jsonschema library (for quality gate validation)

Install dependencies with:
```bash
pip install jsonschema
```

## License

This is a proprietary implementation for internal use.