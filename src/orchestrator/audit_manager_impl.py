# src/orchestrator/audit_manager_impl.py
"""
Implementation of IAuditManager using existing decision log manager.
"""
from typing import List, Optional, Dict, Any
from ..models.artifact_reference import ArtifactReference
from .decision_log import DecisionLogManager
from .audit_manager import IAuditManager


class AuditManagerImpl(IAuditManager):
    """
    Manages logging of workflow events, stage transitions, quality gate decisions, and checkpoints.
    Delegates to DecisionLogManager.
    """

    def __init__(self):
        """Initialize audit manager."""
        self.decision_log_manager = DecisionLogManager()

    def log_workflow_event(
        self,
        workflow_id: str,
        event_type: str,
        description: str,
        related_artifacts: List[ArtifactReference] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a workflow-level event.

        Args:
            workflow_id: The ID of the workflow.
            event_type: The type of event (e.g., 'started', 'completed', 'failed').
            description: A human-readable description of the event.
            related_artifacts: Artifacts related to the event.
            metadata: Additional metadata for the event.
        """
        related_artifacts = related_artifacts or []
        self.decision_log_manager.log_workflow_event(
            workflow_id=workflow_id,
            event_type=event_type,
            description=description,
            related_artifacts=related_artifacts,
            metadata=metadata
        )

    def log_stage_transition(
        self,
        workflow_id: str,
        from_stage: str,
        to_stage: str,
        decision: str,
        rationale: str,
        related_artifacts: List[ArtifactReference] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a stage transition event.

        Args:
            workflow_id: The ID of the workflow.
            from_stage: The stage ID being transitioned from.
            to_stage: The stage ID being transitioned to.
            decision: The decision made (e.g., 'approved', 'failed').
            rationale: The rationale for the decision.
            related_artifacts: Artifacts related to the transition.
            metadata: Additional metadata (e.g., stage execution details).
        """
        related_artifacts = related_artifacts or []
        self.decision_log_manager.log_stage_transition(
            workflow_id=workflow_id,
            from_stage=from_stage,
            to_stage=to_stage,
            decision=decision,
            rationale=rationale,
            related_artifacts=related_artifacts,
            metadata=metadata
        )

    def log_quality_gate_decision(
        self,
        workflow_id: str,
        stage_id: str,
        decision: str,
        rationale: str,
        related_artifacts: List[ArtifactReference] = None
    ) -> None:
        """
        Log a quality gate decision.

        Args:
            workflow_id: The ID of the workflow.
            stage_id: The ID of the stage.
            decision: The decision made by the quality gate.
            rationale: The rationale for the decision.
            related_artifacts: The artifacts that were validated.
        """
        related_artifacts = related_artifacts or []
        self.decision_log_manager.log_quality_gate_decision(
            workflow_id=workflow_id,
            stage_id=stage_id,
            decision=decision,
            rationale=rationale,
            related_artifacts=related_artifacts
        )

    def log_checkpoint_created(
        self,
        workflow_id: str,
        checkpoint_id: str,
        stage_id: str
    ) -> None:
        """
        Log that a checkpoint was created.

        Args:
            workflow_id: The ID of the workflow.
            checkpoint_id: The ID of the checkpoint.
            stage_id: The ID of the stage after which the checkpoint was created.
        """
        self.decision_log_manager.log_workflow_event(
            workflow_id=workflow_id,
            event_type="checkpoint_created",
            description=f"Created checkpoint {checkpoint_id} after stage {stage_id}",
            related_artifacts=[],
            metadata={
                "checkpoint_id": checkpoint_id,
                "stage": stage_id
            }
        )

    def get_decision_log_reference(self, workflow_id: str) -> dict:
        """
        Get a reference to the decision log for checkpointing.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Dictionary with logId and entryCount for checkpoint reference
        """
        return self.decision_log_manager.get_decision_log_reference(workflow_id)