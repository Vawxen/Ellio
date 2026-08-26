# src/orchestrator/workflow_executor.py
"""
Main workflow executor that orchestrates stage execution.
"""

import time
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..models.parameterized_manifest import ParameterizedManifest
from ..models.workflow_state import WorkflowState
from ..models.stage_execution_result import StageExecutionResult
from ..models.artifact_reference import ArtifactReference
from .manifest import ManifestParser
from .dependency_enforcer import DependencyEnforcer
from .handoff_recorder import HandoffRecorder
from ..utils.config import config
from ..utils.storage import storage

# Import the strategy interfaces
from .state_persistence_manager import IStatePersistenceManager
from .execution_validation_manager import IExecutionValidationManager
from .audit_manager import IAuditManager


class WorkflowExecutorError(Exception):
    """Base exception for workflow executor errors."""
    pass


class WorkflowExecutor:
    """
    Main orchestrator that executes workflows according to manifests.
    """

    def __init__(
        self,
        state_persistence_manager: Optional[IStatePersistenceManager] = None,
        execution_validation_manager: Optional[IExecutionValidationManager] = None,
        audit_manager: Optional[IAuditManager] = None
    ):
        """
        Initialize workflow executor with strategy dependencies.
        
        Args:
            state_persistence_manager: Strategy for state persistence (optional, defaults to StatePersistenceManagerImpl)
            execution_validation_manager: Strategy for execution and validation (optional, defaults to ExecutionValidationManagerImpl)
            audit_manager: Strategy for audit logging (optional, defaults to AuditManagerImpl)
        """
        # Set up strategies with defaults for backward compatibility
        self.state_persistence_manager = state_persistence_manager or StatePersistenceManagerImpl()
        self.execution_validation_manager = execution_validation_manager or ExecutionValidationManagerImpl()
        self.audit_manager = audit_manager or AuditManagerImpl()
        
        # Other dependencies that are not yet strategized
        self.manifest_parser = ManifestParser()
        self.dependency_enforcer = DependencyEnforcer  # Note: this is a class, we'll instantiate per use
        self.handoff_recorder = HandoffRecorder()
        self.config = config
        
        # State tracking
        self._current_workflow_id: Optional[str] = None
        self._is_running = False
        self._should_cancel = False
        self._pause_requested = False

    def execute_workflow(self, manifest: ParameterizedManifest,
                         resume_from_checkpoint: bool = False) -> WorkflowState:
        """
        Execute a workflow according to the manifest.
        
        Args:
            manifest: Parameterized manifest to execute
            resume_from_checkpoint: Whether to attempt resuming from a checkpoint
            
        Returns:
            Final workflow state
            
        Raises:
            WorkflowExecutorError: If workflow execution fails
        """
        workflow_id = manifest.workflow_id
        self._current_workflow_id = workflow_id
        
        try:
            # Check if we should resume from checkpoint
            initial_state = None
            resumption_stage = None
            
            if resume_from_checkpoint:
                # Try to load workflow state from persistence manager
                initial_state = self.state_persistence_manager.load_workflow_state(workflow_id)
                if initial_state is not None:
                    # We have a checkpoint, now we need to determine if we can resume
                    # and from which stage.
                    # For simplicity, we'll reuse the ResumeHandler logic via the state persistence manager?
                    # But our state persistence manager doesn't have resumption logic yet.
                    # We'll need to add a method to check if we can resume and get the resumption stage.
                    # However, to keep changes minimal, we'll keep the ResumeHandler for now.
                    # Alternatively, we can extend the state persistence manager.
                    # Given time, we'll leave the ResumeHandler in place and use it here.
                    from .resume_handler import ResumeHandler
                    resume_handler = ResumeHandler()
                    if resume_handler.can_resume_workflow(workflow_id, manifest):
                        initial_state, resumption_stage = resume_handler.resume_workflow(workflow_id, manifest)
                        # Log resumption event
                        self.audit_manager.log_workflow_event(
                            workflow_id=workflow_id,
                            event_type="resumed",
                            description=f"Resumed workflow from checkpoint at stage {resumption_stage}",
                            related_artifacts=[],
                            metadata={"resumption_stage": resumption_stage}
                        )
                    else:
                        # No valid checkpoint found, start fresh
                        initial_state = self.state_persistence_manager.initialize_state(manifest)
                        self.audit_manager.log_workflow_event(
                            workflow_id=workflow_id,
                            event_type="started",
                            description="Started workflow execution",
                            related_artifacts=[],
                            metadata={}
                        )
                else:
                    # No checkpoint found, start fresh
                    initial_state = self.state_persistence_manager.initialize_state(manifest)
                    self.audit_manager.log_workflow_event(
                        workflow_id=workflow_id,
                        event_type="started",
                        description="Started workflow execution",
                        related_artifacts=[],
                        metadata={}
                    )
            else:
                # Start fresh
                initial_state = self.state_persistence_manager.initialize_state(manifest)
                self.audit_manager.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="started",
                    description="Started workflow execution",
                    related_artifacts=[],
                    metadata={}
                )
            
            # Initialize execution state
            workflow_state = initial_state
            workflow_state.status = "running"
            workflow_state.started_at = datetime.utcnow()
            
            # Main execution loop
            while workflow_state.status == "running":
                # Check for cancellation request
                if self._should_cancel:
                    workflow_state.status = "cancelled"
                    break
                
                # Get stages ready for execution
                completed_stages = list(workflow_state.completed_stages)
                # We need to create a DependencyEnforcer instance for the current manifest
                dependency_enforcer = DependencyEnforcer(manifest.stages)
                ready_stages = dependency_enforcer.get_ready_stages(completed_stages)
                
                # Filter out stages that have already been attempted too many times
                executable_stages = []
                for stage in ready_stages:
                    attempts = workflow_state.get_stage_attempts(stage.stage_id)
                    max_attempts = (stage.retry_policy.get("maxAttempts", self.config.get("default_max_attempts", 3)) 
                                  if stage.retry_policy else self.config.get("default_max_attempts", 3))
                    if attempts < max_attempts:
                        executable_stages.append(stage)
                
                # If no stages are executable, check if we're done or waiting
                if not executable_stages:
                    # Check if all stages are completed
                    all_stage_ids = {stage.stage_id for stage in manifest.stages}
                    if set(completed_stages) == all_stage_ids:
                        workflow_state.status = "completed"
                        break
                    
                    # Check if any stage has failed
                    if workflow_state.failed_stage is not None:
                        workflow_state.status = "failed"
                        break
                    
                    # Otherwise, we're waiting for dependencies (shouldn't happen in linear flow)
                    # But just in case, sleep briefly to avoid busy waiting
                    time.sleep(1)
                    continue
                
                # Execute each ready stage
                for stage in executable_stages:
                    # Check for cancellation before each stage
                    if self._should_cancel:
                        workflow_state.status = "cancelled"
                        break
                    
                    # Increment attempt counter
                    workflow_state.increment_stage_attempts(stage.stage_id)
                    
                    # Get input artifacts from workflow state
                    input_artifacts = []
                    for input_ref in stage.inputs:
                        # Try to get the artifact from workflow state outputs
                        try:
                            # Find the most recent version of this artifact in workflow state
                            artifact = self._resolve_input_artifact(input_ref, workflow_state)
                            if artifact:
                                input_artifacts.append(artifact)
                            else:
                                # If we can't resolve it, use the reference as-is (might be an external asset)
                                input_artifacts.append(input_ref)
                        except Exception:
                            # If resolution fails, use the reference as-is
                            input_artifacts.append(input_ref)
                    
                    # Execute the stage using execution strategy
                    stage_result = self.execution_validation_manager.execute_stage(
                        stage_def=stage,
                        workflow_state=workflow_state,
                        manifest=manifest,
                        input_artifacts=input_artifacts
                    )
                    
                    # Validate stage outputs using execution strategy
                    gate_decision = self.execution_validation_manager.validate_stage_outputs(
                        artifacts=stage_result.artifacts_produced,
                        stage_def=stage,
                        manifest=manifest
                    )
                    
                    # Process stage result
                    self._process_stage_result(
                        workflow_id=workflow_id,
                        stage_def=stage,
                        stage_result=stage_result,
                        workflow_state=workflow_state,
                        manifest=manifest,
                        gate_decision=gate_decision
                    )
                    
                    # Check if we should checkpoint after this stage
                    if self._should_checkpoint_after_stage(workflow_state):
                        self._create_checkpoint_if_needed(
                            workflow_id=workflow_id,
                            workflow_state=workflow_state,
                            current_stage=stage.stage_id
                        )
            
            # Finalize workflow state
            workflow_state.updated_at = datetime.utcnow()
            
            # Log completion event
            if workflow_state.status == "completed":
                self.audit_manager.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="completed",
                    description="Workflow completed successfully",
                    related_artifacts=[],
                    metadata={}
                )
            elif workflow_state.status == "failed":
                self.audit_manager.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="failed",
                    description=f"Workflow failed at stage {workflow_state.failed_stage}",
                    related_artifacts=[],
                    metadata={"failed_stage": workflow_state.failed_stage}
                )
            elif workflow_state.status == "cancelled":
                self.audit_manager.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="cancelled",
                    description="Workflow was cancelled",
                    related_artifacts=[],
                    metadata={}
                )
            
            return workflow_state
            
        except Exception as e:
            # Ensure workflow state reflects failure
            if workflow_state is not None:
                workflow_state.status = "failed"
                workflow_state.updated_at = datetime.utcnow()
                if self._current_workflow_id:
                    self.audit_manager.log_workflow_event(
                        workflow_id=self._current_workflow_id,
                        event_type="failed",
                        description=f"Workflow execution failed: {e}",
                        related_artifacts=[],
                        metadata={"error": str(e)}
                    )
            raise WorkflowExecutorError(f"Workflow execution failed: {e}")
        finally:
            self._current_workflow_id = None

    def _create_initial_workflow_state(self, manifest: ParameterizedManifest) -> WorkflowState:
        """
        Create initial workflow state from manifest.
        
        Args:
            manifest: Parameterized manifest
            
        Returns:
            Initial WorkflowState instance
        """
        # This method is now deprecated; use state_persistence_manager.initialize_state instead
        # We keep it for backward compatibility or if needed elsewhere.
        return WorkflowState(
            workflow_id=manifest.workflow_id,
            manifest_version=manifest.manifest_version,
            name=manifest.name,
            description=manifest.description,
            parameters=manifest.parameters.copy()
        )

    def _resolve_input_artifact(self, input_ref: ArtifactReference,
                              workflow_state: WorkflowState) -> Optional[ArtifactReference]:
        """
        Resolve an input artifact reference to an actual artifact from workflow state.
        
        Args:
            input_ref: Input artifact reference to resolve
            workflow_state: Current workflow state
            
        Returns:
            Resolved artifact reference or None if not found
        """
        # Look for this artifact in the outputs of completed stages
        # We prioritize more recent outputs (higher stage execution order)
        for stage_id in reversed(list(workflow_state.completed_stages)):
            outputs = workflow_state.get_stage_outputs(stage_id)
            for output in outputs:
                # Match by artifact type and ID (simplistic matching)
                if (output.artifact_type == input_ref.artifact_type and 
                    output.artifact_id == input_ref.artifact_id):
                    # Return the output with updated location/producer info if needed
                    # In a real implementation, we might want to validate or transform
                    return output
        
        # Not found in workflow state
        return None

    def _process_stage_result(self, workflow_id: str, stage_def: 'StageDefinition',
                            stage_result: StageExecutionResult,
                            workflow_state: WorkflowState,
                            manifest: ParameterizedManifest,
                            gate_decision: Dict[str, Any]) -> None:
        """
        Process the result of a stage execution.
        
        Args:
            workflow_id: ID of the workflow
            stage_def: Stage definition that was executed
            stage_result: Result from stage execution
            workflow_state: Current workflow state to update
            manifest: Workflow manifest
            gate_decision: Decision from quality gate validation
        """
        stage_id = stage_def.stage_id
        
        if stage_result.succeeded:
            # Stage execution succeeded
            # Update artifact validation status to "pending" (will be updated by quality gate)
            validated_outputs = []
            for output in stage_result.artifacts_produced:
                validated_outputs.append(
                    output.with_updated_status("pending")
                )
            
            # Update artifact validation status based on gate decision
            final_outputs = []
            for artifact in validated_outputs:
                if gate_decision["decision"] == "approved":
                    final_outputs.append(
                        artifact.with_updated_status("passed")
                    )
                else:
                    final_outputs.append(
                        artifact.with_updated_status("failed")
                    )
            
            # Mark stage as completed
            workflow_state.mark_stage_completed(stage_id, final_outputs)
            
            # Record handoff of outputs
            self.handoff_recorder.record_stage_output_handoff(
                workflow_id=workflow_id,
                stage_id=stage_id,
                artifacts=final_outputs,
                quality_gate_decision=gate_decision
            )
            
            # Log stage completion and quality gate decision
            self.audit_manager.log_stage_transition(
                workflow_id=workflow_id,
                from_stage=stage_id,
                to_stage="__NEXT_STAGE__",  # Simplified for MVP
                decision=gate_decision["decision"],
                rationale=gate_decision["rationale"],
                related_artifacts=final_outputs,
                metadata={
                    "stage_execution": {
                        "exit_code": stage_result.exit_code,
                        "duration_seconds": stage_result.duration_seconds,
                        "stdout_length": len(stage_result.stdout),
                        "stderr_length": len(stage_result.stderr)
                    }
                }
            )
            
            # Log quality gate decision separately
            self.audit_manager.log_quality_gate_decision(
                workflow_id=workflow_id,
                stage_id=stage_id,
                decision=gate_decision["decision"],
                rationale=gate_decision["rationale"],
                related_artifacts=final_outputs
            )
        else:
            # Stage execution failed
            workflow_state.mark_stage_failed(stage_id)
            
            # Log stage failure
            self.audit_manager.log_workflow_event(
                workflow_id=workflow_id,
                event_type="stage_failed",
                description=f"Stage {stage_id} failed with exit code {stage_result.exit_code}",
                related_artifacts=[],
                metadata={
                    "stage_id": stage_id,
                    "exit_code": stage_result.exit_code,
                    "stdout": stage_result.stdout[:500],  # Limit size
                    "stderr": stage_result.stderr[:500]   # Limit size
                }
            )

    def _should_checkpoint_after_stage(self, workflow_state: WorkflowState) -> bool:
        """
        Determine if a checkpoint should be created after the current stage.
        
        Args:
            workflow_state: Current workflow state
            
        Returns:
            True if checkpoint should be created, False otherwise
        """
        # Checkpoint based on time interval
        # We need to access the checkpoint manager's should_checkpoint method
        # But we don't have a checkpoint manager attribute anymore.
        # We'll create a temporary checkpoint manager instance just for this check.
        # This is not ideal but works for now.
        checkpoint_manager = CheckpointManager()
        return checkpoint_manager.should_checkpoint()

    def _create_checkpoint_if_needed(self, workflow_id: str, workflow_state: WorkflowState,
                                    current_stage: str) -> None:
        """
        Create a checkpoint if needed based on time interval.
        
        Args:
            workflow_id: ID of the workflow
            workflow_state: Current workflow state
            current_stage: Current stage ID
        """
        try:
            # Get decision log reference from audit manager
            decision_log_reference = self.audit_manager.get_decision_log_reference(workflow_id)
            
            # Create checkpoint using checkpoint manager
            checkpoint_manager = CheckpointManager()
            
            # Create checkpoint
            checkpoint = checkpoint_manager.create_checkpoint(
                workflow_state=workflow_state,
                current_step=current_stage,
                decision_log_reference=decision_log_reference
            )
            
            # Log checkpoint creation
            self.audit_manager.log_checkpoint_created(
                workflow_id=workflow_id,
                checkpoint_id=checkpoint.checkpoint_id,
                stage_id=current_stage
            )
        except Exception:
            # Don't let checkpoint failures break stage execution
            # In a production system, we might want to alert on this
            pass

    def cancel(self) -> None:
        """Cancel the currently executing workflow."""
        self._should_cancel = True

    def pause(self) -> None:
        """Pause the currently executing workflow."""
        self._pause_requested = True

    def resume(self) -> None:
        """Resume a paused workflow."""
        self._pause_requested = False