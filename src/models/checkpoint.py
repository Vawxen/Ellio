# src/models/checkpoint.py
"""
Checkpoint model for workflow state persistence.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from .workflow_state import WorkflowState


@dataclass
class Checkpoint:
    """
    Represents a checkpoint of workflow state for resumability.
    """
    checkpoint_id: str
    timestamp: datetime
    workflow_id: str
    current_step: str  # stageId where execution is paused/resumed
    state: WorkflowState
    decision_log_reference: Dict[str, Any]  # Reference to decision log: {logId: str, entryCount: int}
    version: str = "1.0.0"

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.checkpoint_id:
            raise ValueError("checkpoint_id cannot be empty")
        if not self.workflow_id:
            raise ValueError("workflow_id cannot be empty")
        if not self.current_step:
            raise ValueError("current_step cannot be empty")
        if not isinstance(self.state, WorkflowState):
            raise ValueError("state must be a WorkflowState instance")
        if not isinstance(self.decision_log_reference, dict):
            raise ValueError("decision_log_reference must be a dictionary")
        if "logId" not in self.decision_log_reference or "entryCount" not in self.decision_log_reference:
            raise ValueError("decision_log_reference must have 'logId' and 'entryCount' fields")
        if not isinstance(self.decision_log_reference["logId"], str):
            raise ValueError("decision_log_reference.logId must be a string")
        if not isinstance(self.decision_log_reference["entryCount"], int) or self.decision_log_reference["entryCount"] < 0:
            raise ValueError("decision_log_reference.entryCount must be a non-negative integer")

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the checkpoint
        """
        return {
            "checkpointId": self.checkpoint_id,
            "timestamp": self.timestamp.isoformat(),
            "workflowId": self.workflow_id,
            "currentStep": self.current_step,
            "state": self.state.to_dict(),
            "decisionLogReference": self.decision_log_reference,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Checkpoint':
        """
        Create Checkpoint from dictionary.
        
        Args:
            data: Dictionary with checkpoint data
            
        Returns:
            Checkpoint instance
        """
        return cls(
            checkpoint_id=data["checkpointId"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            workflow_id=data["workflowId"],
            current_step=data["currentStep"],
            state=WorkflowState.from_dict(data["state"]),
            decision_log_reference=data["decisionLogReference"],
            version=data.get("version", "1.0.0")
        )