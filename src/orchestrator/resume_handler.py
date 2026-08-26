# src/orchestrator/resume_handler.py
"""
Resume handler for workflow recovery from checkpoints.
"""

from typing import Optional, List
from ..models.checkpoint import Checkpoint
from ..models.workflow_state import WorkflowState
from ..models.parameterized_manifest import ParameterizedManifest
from .checkpoint_manager import CheckpointManager
from .decision_log import DecisionLogManager


class ResumeHandlerError(Exception):
    """Base exception for resume handler errors."""
    pass


class ResumeHandler:
    """
    Handles resuming workflows from checkpoints.
    """
    
    def __init__(self):
        """Initialize resume handler."""
        self.checkpoint_manager = CheckpointManager()
        self.decision_log_manager = DecisionLogManager()
    
    def can_resume_workflow(self, workflow_id: str, 
                           manifest: ParameterizedManifest) -> bool:
        """
        Check if a workflow can be resumed from a checkpoint.
        
        Args.
            workflow_id: ID of the workflow
            manifest: Current manifest for the workflow
            
        Returns:
            True if workflow can be resumed, False otherwise
        """
        try:
            # Check if any checkpoints exist for this workflow
            latest_checkpoint = self.checkpoint_manager.load_latest_checkpoint(workflow_id)
            if latest_checkpoint is None:
                return False
            
            # Check manifest version compatibility
            if latest_checkpoint.state.manifest_version != manifest.manifest_version:
                # In a more advanced implementation, we could check for compatibility
                # For MVP, we require exact version match
                return False
            
            # Check workflow ID matches
            if latest_checkpoint.state.workflow_id != workflow_id:
                return False
            
            # Check workflow name matches (optional but recommended)
            if latest_checkpoint.state.name != manifest.name:
                return False
            
            return True
        except Exception:
            # If any error occurs, assume we cannot resume
            return False
    
    def resume_workflow(self, workflow_id: str,
                       manifest: ParameterizedManifest) -> tuple[WorkflowState, str]:
        """
        Resume a workflow from the latest checkpoint.
        
        Args:
            workflow_id: ID of the workflow
            manifest: Current manifest for the workflow
            
        Returns:
            Tuple of (restored WorkflowState, resumption stage ID)
            
        Raises:
            ResumeHandlerError: If workflow cannot be resumed
        """
        try:
            # Load the latest checkpoint
            latest_checkpoint = self.checkpoint_manager.load_latest_checkpoint(workflow_id)
            if latest_checkpoint is None:
                raise ResumeHandlerError(f"No checkpoint found for workflow {workflow_id}")
            
            # Validate checkpoint compatibility
            if not self.can_resume_workflow(workflow_id, manifest):
                raise ResumeHandlerError(
                    f"Checkpoint for workflow {workflow_id} is incompatible with current manifest"
                )
            
            # Get the workflow state from checkpoint
            workflow_state = latest_checkpoint.state
            
            # Determine resumption point
            resumption_stage = self._determine_resumption_point(
                workflow_state, manifest
            )
            
            # Validate decision log consistency
            self._validate_decision_log_consistency(
                workflow_id, latest_checkpoint.decision_log_reference
            )
            
            return workflow_state, resumption_stage
        except Exception as e:
            if isinstance(e, ResumeHandlerError):
                raise
            raise ResumeHandlerError(f"Failed to resume workflow {workflow_id}: {e}")
    
    def _determine_resumption_point(self, workflow_state: WorkflowState,
                                  manifest: ParameterizedManifest) -> str:
        """
        Determine where to resume execution based on completed stages.
        
        Args:
            workflow_state: Restored workflow state
            manifest: Current manifest
            
        Returns:
            Stage ID to resume from
        """
        completed_stages = set(workflow_state.completed_stages)
        
        # If all stages are completed, workflow is done
        all_stage_ids = {stage.stage_id for stage in manifest.stages}
        if completed_stages == all_stage_ids:
            # All stages completed, return a special value indicating completion
            return "__WORKFLOW_COMPLETE__"
        
        # Find the first incomplete stage whose dependencies are satisfied
        # This is where we should resume execution
        for stage in manifest.stages:
            if stage.stage_id not in completed_stages:
                # Check if dependencies are satisfied
                dependencies_satisfied = all(
                    dep in completed_stages for dep in stage.depends_on
                )
                if dependencies_satisfied:
                    return stage.stage_id
                # If dependencies aren't satisfied, we need to wait for them to complete
                # But since we're resuming, this shouldn't happen if checkpoint was taken correctly
        
        # Fallback: return the first incomplete stage
        for stage in manifest.stages:
            if stage.stage_id not in completed_stages:
                return stage.stage_id
        
        # This shouldn't happen if we checked for completion above
        return manifest.stages[0].stage_id if manifest.stages else ""
    
    def _validate_decision_log_consistency(self, workflow_id: str,
                                         decision_log_reference: dict) -> None:
        """
        Validate that the decision log reference in the checkpoint matches actual state.
        
        Args:
            workflow_id: ID of the workflow
            decision_log_reference: Reference from checkpoint (logId and entryCount)
            
        Raises:
            ResumeHandlerError: If decision log reference is inconsistent
        """
        try:
            # Get actual entry count from storage
            actual_entry_count = self.decision_log_manager.get_decision_log_entry_count(workflow_id)
            expected_entry_count = decision_log_reference.get("entryCount", 0)
            
            # For resumption, we expect the actual count to be >= expected count
            # (it could be greater if additional logging happened after checkpoint)
            if actual_entry_count < expected_entry_count:
                raise ResumeHandlerError(
                    f"Decision log entry count mismatch: expected at least {expected_entry_count}, "
                    f"found {actual_entry_count}"
                )
            
            # Validate log ID matches workflow ID (in our implementation)
            if decision_log_reference.get("logId") != workflow_id:
                raise ResumeHandlerError(
                    f"Decision log reference logId mismatch: expected {workflow_id}, "
                    f"found {decision_log_reference.get('logId')}"
                )
        except Exception as e:
            if isinstance(e, ResumeHandlerError):
                raise
            raise ResumeHandlerError(f"Failed to validate decision log consistency: {e}")
    
    def get_resumable_workflows(self) -> List[str]:
        """
        Get list of workflow IDs that have checkpoints and can potentially be resumed.
        
        Returns:
            List of workflow IDs with available checkpoints
        """
        try:
            checkpoint_ids = self.checkpoint_manager.storage.list_checkpoints()
            workflow_ids = set()
            
            for checkpoint_id in checkpoint_ids:
                try:
                    checkpoint = self.checkpoint_manager.storage.load_checkpoint(checkpoint_id)
                    workflow_ids.add(checkpoint.state.workflow_id)
                except Exception:
                    # Skip corrupted checkpoints
                    continue
            
            return list(workflow_ids)
        except Exception:
            return []