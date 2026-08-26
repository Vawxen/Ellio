# Manifest-Driven Video Pipeline Architecture Specification

## 1. Overview

The manifest-driven video pipeline orchestration spine provides a flexible, resilient framework for executing multi-stage video processing workflows. Workflows are defined declaratively in JSON manifests, enabling dynamic workflow composition, parameter substitution, and automated dependency management.

Key characteristics:
- **Manifest-Driven**: Workflow logic encoded in JSON manifests
- **Resilient**: Persistent checkpointing enables recovery from failures
- **Audit-ready**: Structured handoffs and decision logging provide complete traceability
- **Extensible**: Supports custom stage types, quality gates, and artifact types
- **Parameterized**: Manifests can use runtime parameters for reuse across environments

## 2. Core Components

### 2.1 Manifest Parser & Validator
Located in `src/orchestrator/manifest.py`, responsible for:
- Parsing JSON manifests into internal data models
- Validating manifest structure against schema
- Performing parameter substitution
- Handling manifest versioning

### 2.2 Data Models
Defined in `src/models/`:
- **ArtifactReference**: Immutable reference to pipeline artifacts
- **StageDefinition**: Configuration for individual pipeline stages
- **WorkflowState**: Runtime tracking of workflow execution progress
- **Checkpoint**: Persistent workflow state snapshots
- **DecisionLogEntry**: Audit trail of workflow decisions and events
- **ValidationResult**: Outcome of quality gate evaluations
- **StageExecutionResult**: Results from stage execution attempts

### 2.3 Orchestration Engine
Located in `src/orchestrator/`:
- **StageRunner**: Executes stages as command-line processes
- **DependencyEnforcer**: Resolves stage dependencies via topological sorting
- **CheckpointManager**: Handles workflow state persistence and restoration
- **DecisionLogManager**: Records audit trail entries
- **QualityGateEngine**: Executes artifact validation against schemas
- **HandoffRecorder**: Documents artifact transfers between stages
- **WorkflowExecutor**: Main orchestration loop coordinating stage execution
- **ResumeHandler**: Manages workflow recovery from checkpoints

### 2.4 Utilities
Located in `src/utils/`:
- **Validation helpers**: Schema validation utilities
- **Configuration management**: Environment and file-based configuration
- **Storage abstraction**: Filesystem-based storage for artifacts and state

## 3. Stage Definitions

### 3.1 StageDefinition Model
The `StageDefinition` class (src/models/stage_definition.py) represents a pipeline stage as defined in the manifest:

#### Fields:
- `stage_id` (string): Unique identifier within the workflow
- `agent_role` (string): Command or script to execute for this stage
- `depends_on` (list[string]): Stage IDs that must complete before this stage
- `inputs` (list[ArtifactReference]): Artifacts consumed by this stage
- `outputs` (list[ArtifactReference]): Artifacts produced by this stage
- `quality_gates` (list[dict]): Validation checks to perform on outputs
- `timeout_seconds` (optional[int]): Maximum execution time in seconds
- `retry_policy` (optional[dict]): Retry configuration with `maxAttempts` and `backoffSeconds`

#### Validation Rules:
- Stage ID and agent role must be non-empty strings
- Dependencies must be a list of non-empty strings
- Inputs and outputs must be lists of valid ArtifactReference instances
- Quality gates must be dictionaries containing `gateId` and `type` fields
- Timeout seconds must be a positive integer if provided
- Retry policy must contain non-negative integers for `maxAttempts` and `backoffSeconds`

#### Methods:
- `is_ready(completed_stages)`: Determines if dependencies are satisfied
- `to_dict()`/`from_dict()`: Serialization/deserialization for manifest parsing

### 3.2 Stage Execution
Stages are executed as command-line processes by the StageRunner:
- The `agent_role` field is treated as the command to execute
- Standard input/output/streams are captured for logging
- Exit code determines success (0) or failure (non-zero)
- Environment variables are populated with workflow context
- Artifact locations are made available via environment variables or manifest substitution

## 4. Artifact Contracts

### 4.1 ArtifactReference Model
The `ArtifactReference` class (src/models/artifact_reference.py) defines the contract for pipeline artifacts:

#### Fields:
- `artifact_type` (string): Categorization of artifact (e.g., "video", "transcript")
- `artifact_id` (string): Unique identifier for the artifact instance
- `version` (string): Semantic version of the artifact format
- `location` (string): URI indicating artifact storage location
- `producer_stage` (string): Stage ID that produced this artifact
- `validation_status` (string): One of ["pending", "passed", "failed", "skipped"]

#### Validation Rules:
- All string fields must be non-empty
- Validation status must be one of the allowed values
- Immutable after creation (except validation status via `with_updated_status`)

#### Methods:
- `with_updated_status(status)`: Returns new instance with updated validation status
- `to_dict()`/`from_dict()`: Conversion to/from dictionary representation

### 4.2 Artifact URI Scheme
Artifact locations use URI schemes to indicate storage mechanism:
- `file://`: Filesystem paths (absolute or relative)
- `s3://`: Amazon S3 storage
- `gcs://`: Google Cloud Storage
- `azure://`: Azure Blob Storage
- `http://`/`https://`: HTTP-accessible resources

### 4.3 Artifact Lifecycle
1. **Consumption**: Stage declares artifact in inputs with expected type/ID/version
2. **Production**: Stage produces artifact and records in outputs
3. **Validation**: Quality gates validate produced artifacts
4. **Consumption**: Downstream stages reference produced artifacts by ID
5. **Archival**: Artifacts retained according to configured policies

### 4.4 Artifact Types for Video Pipeline
Common artifact types in video processing workflows:
- `video`: Raw or processed video files (formats: mp4, mov, avi, etc.)
- `audio`: Extracted or processed audio tracks
- `transcript`: Speech-to-text output (formats: json, srt, vtt)
- `translated-transcript`: Translated text content
- `subtitles`: Formatted subtitle files (srt, vtt, ass)
- `thumbnail`: Keyframe images (formats: jpg, png)
- `metadata`: Technical or descriptive metadata (formats: json, xml)
- `proxy`: Lower-resolution video copies for preview

## 5. Integration Points

### 5.1 Stage-to-Stage Data Flow
Artifacts flow between stages through the following mechanism:
1. Upstage stage produces artifacts and records them in its outputs
2. Orchestrator records handoff via HandoffRecorder
3. Downstream stage declares matching artifacts in its inputs
4. DependencyEnforcer ensures upstream completion before downstream execution
5. Artifact references are made available to stage via environment or manifest substitution

### 5.2 Quality Gate Integration
Quality gates are integrated at multiple points:
- **Per-stage gates**: Defined in stage's `qualityGates` array, executed after stage completion
- **Global gates**: Defined in manifest's `globalQualityGates`, executed after workflow completion
- **Gate types**: Extensible validation mechanisms (currently schemaValidation)
- **Validation artifacts**: Quality gates consume ArtifactReference and produce ValidationResult
- **Failure handling**: Failed quality gates can trigger stage failure or workflow abortion based on configuration

### 5.3 Checkpointing Mechanism
Checkpoints provide workflow resilience:
- **Trigger**: Periodic intervals or after each stage completion (configurable)
- **Content**: Complete WorkflowState serialized to JSON
- **Storage**: Filesystem-based in configured checkpoint directory
- **Resume**: `--resume` flag restores latest checkpoint and continues execution
- **Retention**: Configurable retention policies prevent indefinite storage growth

### 5.4 Decision Logging
Complete audit trail maintained through:
- **Events**: Stage start/completion/failure, quality gate evaluations, checkpoint operations
- **Entries**: Timestamped, structured log entries with contextual data
- **Storage**: Filesystem-based in configured decision log directory
- **Querying**: Designed for integration with log analysis systems

### 5.5 Error Handling & Retry Policies
Robust failure management:
- **Stage-level retries**: Configurable per stage via `retryPolicy`
- **Timeout enforcement**: Automatic termination of long-running stages
- **Failure propagation**: Failed stages mark workflow as failed unless retry succeeds
- **Dead letter queues**: Repeatedly failing stages can be routed for manual intervention
- **Compensation actions**: Optional rollback stages for cleanup on failure

### 5.6 Configuration Integration
Multiple configuration sources:
- **Environment variables**: Prefixed with `ORCHESTRATION_`
- **Configuration files**: JSON files via `--config` argument
- **Programmatic defaults**: `src/utils/config.py`
- **Manifest overrides**: Specific values can override global configuration

## 6. Manifest Format Specification

### 6.1 Root Structure
```jsonc
{
  "manifestVersion": "string (required)",
  "workflowId": "string (required)",
  "name": "string (required)",
  "description": "string (optional)",
  "parameters": { "object (optional)" },
  "stages": [ "StageDefinition array (required)" ],
  "globalQualityGates": [ "QualityGate array (optional)" ]
}
```

### 6.2 Field Details
- `manifestVersion`: Semantic version of manifest schema (currently "1.0.0")
- `workflowId`: Unique identifier for workflow execution instance
- `name`: Human-readable workflow name
- `description`: Detailed workflow description
- `parameters`: Key-value pairs for manifest parameter substitution
- `stages`: Ordered list of stage definitions (execution order determined by dependencies)
- `globalQualityGates`: Validation checks applied to workflow outputs

### 6.3 Parameter Substitution
Manifests support parameter substitution using handlebars-style syntax:
- `{{parameterName}}` replaced with value from parameters object
- Supports nested parameter access: `{{config.value}}`
- Escaping: `{{{parameterName}}}` for raw insertion
- Default values: `{{parameterName "default"}}`

### 6.4 Stage Definition Fields
Each stage object contains:
```jsonc
{
  "stageId": "string (required)",
  "agentRole": "string (required)",
  "dependsOn": ["string"] (optional, default: []),
  "inputs": [ "ArtifactReference array" ] (optional, default: []),
  "outputs": [ "ArtifactReference array" ] (optional, default: []),
  "qualityGates": [ "QualityGate array" ] (optional, default: []),
  "timeoutSeconds": "integer (optional)",
  "retryPolicy": {
    "maxAttempts": "integer (optional, default: 1)",
    "backoffSeconds": "integer (optional, default: 0)"
  } (optional)
}
```

### 6.5 ArtifactReference Fields
Each artifact reference contains:
```jsonc
{
  "artifactType": "string (required)",
  "artifactId": "string (required)",
  "version": "string (required)",
  "location": "string (required)",
  "producerStage": "string (required for outputs, optional for inputs)",
  "validationStatus": "string (optional, default: \"pending\")"
}
```

### 6.6 Quality Gate Fields
Each quality gate contains:
```jsonc
{
  "gateId": "string (required)",
  "type": "string (required, currently: \"schemaValidation\")",
  "config": {
    "schemaUri": "string (required for schemaValidation type)"
  } (required)
}
```

## 7. Extension Mechanisms

### 7.1 Adding New Stage Types
To implement a custom stage type:
1. Develop command-line executable or script that processes artifacts
2. Ensure stage reads input artifacts from declared locations
3. Ensure stage writes output artifacts to declared locations
4. Reference the executable via `agentRole` in manifest
5. Handle artifact URIs appropriately (download/upload if needed)
6. Exit with code 0 for success, non-zero for failure

### 7.2 Adding New Quality Gate Types
To implement a custom quality gate type:
1. Extend `QualityGateEngine.validate_artifact()` method in `src/orchestrator/quality_gate.py`
2. Add handling for new gate type string
3. Implement validation logic consuming ArtifactReference
4. Return ValidationResult with appropriate status and details
5. Reference new gate type in manifest's `qualityGates` arrays

### 7.3 Adding New Artifact Types
To introduce a new artifact type:
1. Define naming convention and semantic meaning
2. Establish versioning scheme for format evolution
3. Document expected file formats and validation criteria
4. Update any schema files used for schemaValidation gates
5. Ensure producing/consuming stages handle the new type appropriately

### 7.4 Adding New Storage Backends
To add a new artifact storage mechanism:
1. Extend storage abstraction in `src/utils/storage.py`
2. Implement `StorageInterface` for new backend
3. Update URI scheme parsing to recognize new scheme
4. Configure credentials and connection parameters via configuration
5. Test with various artifact types and sizes

## 8. Operational Considerations

### 8.1 Deployment Requirements
- Python 3.7+
- jsonschema library (`pip install jsonschema`)
- Access to configured storage backends (filesystem, S3, etc.)
- Sufficient disk space for checkpoint and artifact storage
- Network connectivity for remote storage and external services

### 8.2 Monitoring & Observability
- Decision logs provide execution timeline
- Checkpoint metadata indicates progress
- Artifact handoff records enable traceability
- Integration with metrics systems via extension points
- Health check endpoints available for container orchestration

### 8.3 Scaling Characteristics
- Horizontal scaling: Multiple workflow instances can run concurrently
- Vertical scaling: Resource allocation per stage depends on agent_role
- Bottlenecks: Typically stage execution rather than orchestration overhead
- Resource isolation: Stages run as separate processes

### 8.4 Security Considerations
- Artifact locations may contain sensitive information
- Command execution requires validation of agent_role inputs
- Storage credentials should be managed via secure configuration
- Consider sandboxing for untrusted stage execution
- Audit trails may contain PII and require appropriate protection

## 9. Example Implementation: Video Processing Pipeline

### 9.1 Workflow Description
Typical video processing pipeline demonstrating:
- Ingest: Video file validation and preparation
- Transcription: Speech-to-text conversion
- Translation: Language translation of transcript
- Subtitle Generation: Creating subtitle files from translated transcript

### 9.2 Manifest Example
See `manifests/example.json` for complete example.

### 9.3 Artifact Flow
```
[source-video] -> (ingest) -> [ingested-video]
[ingested-video] -> (transcription) -> [video-transcript]
[video-transcript] -> (translation) -> [translated-transcript]
[translated-transcript] -> (subtitle-generation) -> [video-subtitles]
```

### 9.4 Quality Gates
Each stage validates its output artifact against a JSON schema:
- Ingest: Validates video artifact schema
- Transcription: Validates transcript artifact schema
- Translation: Validates translated transcript artifact schema
- Subtitle Generation: Validates subtitle artifact schema
- Global: Validates universal artifact schema

## 10. Future Enhancements

### 10.1 Planned Features
- Dynamic stage scaling based on workload
- Machine learning model integration stages
- Real-time workflow monitoring dashboard
- Advanced artifact lineage tracking
- Cross-workflow artifact sharing
- Workflow templating and library management

### 10.2 Research Areas
- Workflow optimization algorithms
- Predictive stage duration estimation
- Adaptive retry policies based on error patterns
- Federated execution across distributed orchestrators
- Blockchain-based artifact provenance

## 11. Conclusion

The manifest-driven video pipeline orchestrator provides a robust foundation for building complex video processing workflows. Its declarative manifest approach, combined with resilient execution mechanics and extensive extension points, enables teams to create maintainable, scalable video processing systems while maintaining full auditability and operational control.

The architecture separates concerns effectively: manifest definition describes *what* to do, the orchestration engine handles *how* to execute it, and artifact contracts ensure reliable data flow between stages. This separation enables independent evolution of workflow logic, execution infrastructure, and artifact formats.

---

*Specification Version: 1.0.0*
*Last Updated: 2026-08-19*