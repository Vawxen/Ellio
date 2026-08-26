# MVP Orchestration Spine Implementation Plan

## Context
This plan describes the implementation of the MVP orchestration spine for a manifest-driven multi-agent video pipeline. The orchestrator will provide:
- Manifest-driven stage execution with parameterization support
- Persistent checkpointing for resumability
- Structured handoffs between stages
- One basic quality gate (schema validation)
- Compatibility with the parallel ingestion workstream through clear separation of concerns

## Key Decisions Made

### Architecture Overview
- **Manifest-Driven**: Workflow defined in a declarative manifest file supporting parameterization
- **Stage-Based**: Pipeline consists of discrete stages with explicit dependencies
- **Event-Driven Transitions**: Stage completion triggers quality gates and handoffs
- **Persistent State**: Checkpoints capture workflow state for resumability
- **Artifact-Centric**: Data flows as typed artifact references between stages
- **Loose Coupling**: Orchestration layer separates workflow control from stage implementation

### Contract Definitions
1. **Artifact Reference**: Minimum shape with artifactType, artifactId, version, location, producerStage, validationStatus
2. **Manifest Stage**: stageId, agentRole, dependsOn, inputs, outputs, qualityGates
3. **Decision Log**: timestamp, stageId, decision, rationale, relatedArtifacts
4. **Validation**: Generic schema validation as the MVP quality gate

### Key Improvements from Initial Plan
- **Manifest Parameterization**: Support for input parameters to enable manifest reuse
- **Stage Invocation Mechanism**: Defined command-line execution for MVP with extensible design
- **Agent Resolution**: Clear mapping from agentRole to stage implementations
- **Decision Log Storage**: Separate concern from checkpoints for better performance
- **Enhanced Error Handling**: Granular error reporting and recovery mechanisms

### Assumptions
- Stages are implemented as invokable command-line executables or scripts
- Artifact resolution handled by stages referencing external asset management systems
- Checkpoint/handoff storage via local filesystem (MVP) with path configuration
- Linear stage sequences for MVP (foundation for future DAG support)
- Orchestrator receives manifest file path and optional parameters as input
- Ingestion workstream manages asset_manifest; orchestration manifest references assets by ID

## Implementation Tasks

### Phase 1: Core Infrastructure
1. **Manifest Parser & Validator** (`src/orchestrator/manifest.py`)
   - Parse JSON manifest according to defined format
   - Validate manifest structure, version compatibility, and parameter usage
   - Support parameter substitution (e.g., `{{input_video_path}}`)
   - Provide typed access to manifest data and resolved stage configurations
   - Handle manifest versioning with backward compatibility

2. **Data Models** (`src/models/`)
   - ArtifactReference model (immutable)
   - StageDefinition model (parsed from manifest)
   - ParameterizedManifest model (raw manifest + parameters)
   - WorkflowState model (execution progress, completed stages)
   - Checkpoint model (workflow state snapshot)
   - HandoffRecord model (artifact transfer documentation)
   - DecisionLogEntry model (immutable audit trail)
   - ValidationResult model (quality gate output)
   - StageExecutionResult model (stdout/stderr, exit code, timing)

### Phase 2: Orchestration Engine
3. **Stage Runner** (`src/orchestrator/stage_runner.py`)
   - Execute stages via command-line invocation (primary MVP mechanism)
   - Abstract stage executor interface for future API/message queue support
   - Manage stage timeouts, retry policies, and resource limits
   - Capture stdout/stderr, exit codes, and execution timing
   - Track stage execution status (pending, running, completed, failed)
   - Support stage-specific environment variable injection

4. **Dependency Enforcer** (`src/orchestrator/dependency_enforcer.py`)
   - Resolve stage dependencies using topological sorting
   - Determine when stages are ready to execute based on completed dependencies
   - Detect and report circular dependencies
   - Support dynamic readiness re-evaluation as stages complete
   - Provide execution-ready stage sets to the orchestrator loop

### Phase 3: State Management
5. **Checkpoint Manager** (`src/orchestrator/checkpoint_manager.py`)
   - Persist workflow state to checkpoint storage (JSON files in MVP)
   - Load workflow state from checkpoints for resumption
   - Manage checkpoint lifecycle (creation, cleanup based on retention policy)
   - Store minimal essential state: completed stages, outputs, execution metadata
   - Integrate with decision log via references (not duplication)
   - Support atomic checkpoint writes to prevent corruption

6. **Decision Log Manager** (`src/orchestrator/decision_log.py`)
   - Maintain append-only decision log (JSON lines format)
   - Record quality gate validations, stage transitions, and workflow events
   - Provide efficient querying by workflowId, timestamp, stageId
   - Support log rotation and archiving for long workflows
   - Integrate with checkpoints via logId and entryCount references
   - Ensure immutability and integrity of audit trail

7. **Resume Handler** (`src/orchestrator/resume_handler.py`)
   - Detect existing checkpoints on workflow start
   - Validate checkpoint compatibility with current manifest
   - Restore workflow state from latest valid checkpoint
   - Determine resumption point based on completed stages
   - Re-validate artifacts if needed based on freshness policies
   - Handle resume-from-failure scenarios with appropriate safeguards

### Phase 4: Quality Gates & Handoffs
8. **Quality Gate Engine** (`src/orchestrator/quality_gate.py`)
   - Implement schema validation quality gate (MVP) using jsonschema library
   - Execute validation on artifact references before and after stage execution
   - Produce detailed validation results with field-level error reporting
   - Make proceed/block decisions based on validation outcomes
   - Update artifact validationStatus in workflow state
   - Support pluggable validator architecture for future artifact-specific checks

9. **Handoff Recorder** (`src/orchestrator/handoff_recorder.py`)
   - Create immutable handoff records between stages
   - Link handoffs to specific quality gate decisions via decision log references
   - Persist handoff records as JSON files with efficient querying
   - Maintain artifact lineage and transformation history
   - Support handoff enumeration by workflow, stage, or time range
   - Ensure handoff immutability once created

### Phase 5: Orchestration Logic
10. **Workflow Executor** (`src/orchestrator/workflow_executor.py`)
    - Main orchestration loop coordinating all components
    - Parse manifest and parameters, initialize workflow state
    - Manage execution lifecycle: pending → running → completed/failed/cancelled
    - Schedule stages based on dependency resolution
    - Coordinate stage execution, quality gates, and state updates
    - Handle checkpointing at configurable intervals
    - Manage error recovery, retry logic, and failure escalation

11. **Main Orchestrator** (`src/orchestrator/orchestrator.py`)
    - Command-line interface entry point
    - Parse arguments: manifest path, parameters, runtime options
    - Initialize workflow executor and launch execution
    - Handle graceful shutdown and signal processing
    - Provide progress reporting and observability hooks
    - Return appropriate exit codes for integration with external systems

### Phase 6: Configuration & Utilities
12. **Configuration Manager** (`src/orchestrator/config.py`)
    - Manage runtime configuration (storage paths, timeouts, retry defaults)
    - Support configuration files, environment variables, and defaults
    - Validate configuration values and provide helpful error messages
    - Enable environment-specific configurations (dev, test, prod)

13. **Storage Abstraction** (`src/orchestrator/storage.py`)
    - Abstract storage operations for checkpoints, handoffs, decision logs
    - MVP implementation: local filesystem with configurable base paths
    - Interface designed for future extension to cloud storage (S3, GCS, etc.)
    - Handle path normalization, permissions, and atomic operations

14. **Observability & Logging** (`src/orchestrator/observability.py`)
    - Structured logging with correlation IDs for workflow tracing
    - Metrics collection (stage duration, throughput, success rates)
    - Health check endpoints for external monitoring
    - Debug tracing capabilities for complex workflows

### Phase 7: Integration & Validation
15. **Integration Tests** (`tests/integration/`)
    - Test end-to-end workflow execution with real stage simulators
    - Verify checkpoint creation, resumption, and correctness
    - Validate quality gate blocking and artifact flow
    - Test error scenarios and recovery mechanisms
    - Confirm handoff record creation and decision log integrity

16. **Example Implementation** (`examples/`)
    - Complete end-to-end example demonstrating video processing pipeline
    - Simulated stages: ingest → transcribe → translate → subtitle generation
    - Parameterized manifest showing reuse with different input videos
    - Dockerfile or setup instructions for easy deployment
    - Validation scripts to confirm correct operation

## Risks & Mitigation

### Integration Risks with Ingestion Workstream
- **Manifest Format Misalignment**: 
  - Mitigation: Orchestration manifest focuses exclusively on workflow control
  - Asset metadata remains in asset_manifest; orchestration references by ID
  - Clear documentation of interface boundaries between systems

- **Artifact Reference Mismatch**:
  - Mitigation: Use exact Artifact Reference Contract from shared docs
  - Joint validation of interpretation with ingestion workstream team
  - Location field designed to accommodate URI formats from various storage systems

- **Storage System Conflicts**:
  - Mitigation: Configurable storage prefixes/namespaces
  - Orchestration uses `orchestration/` prefix; ingestion uses `assets/` prefix
  - Separate configuration for storage backends if needed

### Technical Risks
- **Stage Idempotency**:
  - Mitigation: Explicit requirement for stages to handle replay safely
  - Checkpoints capture minimal state; stages should be designed for restart
  - Consider unique output identifiers to prevent conflicts in shared storage

- **Checkpoint Performance**:
  - Mitigation: Asynchronous checkpointing where workflow progress allows
  - State size optimization: only essential execution metadata, not asset data
  - Configurable checkpoint frequency based on workflow criticality

- **Parameter Security**:
  - Mitigation: Sanitize parameter values to prevent injection attacks
  - Support for sensitive parameter handling (secrets management)
  - Audit logging of parameter usage for security review

## Validation Steps

### Unit Testing
- Test manifest parsing with parameter substitution and validation
- Validate topological sorting and dependency resolution algorithms
- Test checkpoint serialization/deserialization with integrity checks
- Verify quality gate decision logic with various validation outcomes
- Confirm handoff record creation and linking to decision log entries
- Test storage abstraction layer with filesystem operations

### Integration Testing
- Execute parameterized workflow with stage simulators
- Verify stage transitions occur correctly based on dependencies
- Test checkpoint creation at intervals and resumption from various points
- Validate quality gate blocking behavior with intentional validation failures
- Confirm handoff records are created, linked, and queryable
- Test decision log integrity and immutability guarantees

### End-to-End Testing
- Run complete parameterized manifest (ingest → transcribe → translate → subtitle)
- Verify all stages execute in correct order with proper parameter passing
- Check that artifacts flow correctly between stages with version tracking
- Validate final outputs match expectations and are properly versioned
- Test failure scenarios: stage failures, timeout handling, retry exhaustion
- Validate recovery mechanisms: checkpoint resumption, manual intervention points

## Open Questions
1. **Stage Containerization**: Should stages be executed directly, in Docker containers, or via another isolation mechanism for MVP?
2. **Asset Freshness**: How should the system handle potentially stale asset references when resuming from checkpoints?
3. **Manifest Complexity**: What level of manifest complexity (conditionals, loops) should be supported beyond the linear MVP?
4. **Production Readiness**: What additional features (metrics, alerting, auth) are needed for production deployment beyond MVP?
5. **Workflow Versioning**: How should workflow definition evolution be managed when manifests are updated?

## Deliverables Upon Completion
- Working orchestrator that executes parameterized manifests with resumability
- Persistent checkpointing with decision log integration
- Structured handoff records maintaining artifact lineage
- One enforced quality gate (schema validation) with extensible design
- Clear documentation of integration assumptions with ingestion workstream
- Example manifest demonstrating end-to-end video processing with parameters
- Comprehensive test suite validating core functionality

This plan is implementation-ready and can be executed by a capable agent following the outlined tasks in sequence.