# src/models/workflow_state.py
"""
Workflow state model for tracking execution progress.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .artifact_reference import ArtifactReference
from .stage_definition import StageDefinition


@dataclass
class WorkflowState:
    """
    Tracks the execution state of a workflow.
    """
    workflow_id: str
    manifest_version: str
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    completed_stages: List[str] = field(default_factory=list)
    failed_stage: Optional[str] = None
    stage_outputs: Dict[str, List[ArtifactReference]] = field(default_factory=dict)
    stage_attempts: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Status
    status: str = "pending"  # pending, running, completed, failed, cancelled

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.workflow_id:
            raise ValueError("workflow_id cannot be empty")
        if not self.manifest_version:
            raise ValueError("manifest_version cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        
        valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
        if self.status not in valid_statuses:
            raise ValueError(
                f"status must be one of: {', '.join(valid_statuses)}. "
                f"Got: {self.status}"
            )
        
        # Validate completed_stages
        if not isinstance(self.completed_stages, list):
            raise ValueError("completed_stages must be a list")
        for stage_id in self.completed_stages:
            if not isinstance(stage_id, str):
                raise ValueError("completed_stages items must be strings")
        
        # Validate stage_outputs
        if not isinstance(self.stage_outputs, dict):
            raise ValueError("stage_outputs must be a dictionary")
        for stage_id, outputs in self.stage_outputs.items():
            if not isinstance(stage_id, str):
                raise ValueError("stage_outputs keys must be strings")
            if not isinstance(outputs, list):
                raise ValueError("stage_outputs values must be lists")
            for output in outputs:
                if not isinstance(output, ArtifactReference):
                    raise ValueError("stage_outputs items must be ArtifactReference instances")
        
        # Validate stage_attempts
        if not isinstance(self.stage_attempts, dict):
            raise ValueError("stage_attempts must be a dictionary")
        for stage_id, attempts in self.stage_attempts.items():
            if not isinstance(stage_id, str):
                raise ValueError("stage_attempts keys must be strings")
            if not isinstance(attempts, int) or attempts < 0:
                raise ValueError("stage_attempts values must be non-negative integers")

    def mark_stage_completed(self, stage_id: str, outputs: List[ArtifactReference]) -> None:
        """
        Mark a stage as completed and record its outputs.
        
        Args:
            stage_id: ID of the stage that completed
            outputs: List of artifact references produced by the stage
        """
        if stage_id in self.completed_stages:
            raise ValueError(f"Stage {stage_id} is already marked as completed")
        
        self.completed_stages.append(stage_id)
        self.stage_outputs[stage_id] = outputs
        self.updated_at = datetime.utcnow()
        
        # If this was the failed stage, clear the failure
        if self.failed_stage == stage_id:
            self.failed_stage = None

    def mark_stage_failed(self, stage_id: str) -> None:
        """
        Mark a stage as failed.
        
        Args:
            stage_id: ID of the stage that failed
        """
        self.failed_stage = stage_id
        self.status = "failed"
        self.updated_at = datetime.utcnow()

    def increment_stage_attempts(self, stage_id: str) -> int:
        """
        Increment the attempt counter for a stage.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            New attempt count
        """
        current = self.stage_attempts.get(stage_id, 0)
        self.stage_attempts[stage_id] = current + 1
        return self.stage_attempts[stage_id]

    def get_stage_attempts(self, stage_id: str) -> int:
        """
        Get the number of attempts for a stage.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            Number of attempts (0 if never attempted)
        """
        return self.stage_attempts.get(stage_id, 0)

    def get_stage_outputs(self, stage_id: str) -> List[ArtifactReference]:
        """
        Get the outputs of a completed stage.
        
        Args:
            stage_id: ID of the stage
            
        Returns:
            List of artifact references produced by the stage
            
        Raises:
            ValueError: If stage has not completed
        """
        if stage_id not in self.completed_stages:
            raise ValueError(f"Stage {stage_id} has not completed")
        return self.stage_outputs.get(stage_id, [])

    def is_stage_completed(self, stage_id: str) -> bool:
        """
        Check if a stage has completed successfully.
        
        Args:
            stage_id: ID of the stage to check
            
        Returns:
            True if stage completed, False otherwise
        """
        return stage_id in self.completed_stages

    def is_stage_failed(self, stage_id: str) -> bool:
        """
        Check if a stage has failed.
        
        Args:
            stage_id: ID of the stage to check
            
        Returns:
            True if stage failed, False otherwise
        """
        return self.failed_stage == stage_id

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for checkpointing.
        
        Returns:
            Dictionary representation of the workflow state
        """
        return {
            "workflowId": self.workflow_id,
            "manifestVersion": self.manifest_version,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "completedStages": self.completed_stages,
            "failedStage": self.failed_stage,
            "stageOutputs": {
                stage_id: [output.to_dict() for output in outputs]
                for stage_id, outputs in self.stage_outputs.items()
            },
            "stageAttempts": self.stage_attempts,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'WorkflowState':
        """
        Create WorkflowState from dictionary (e.g., from checkpoint).
        
        Args:
            data: Dictionary with workflow state data
            
        Returns:
            WorkflowState instance
        """
        # Convert stageOutputs from dict of dicts to dict of ArtifactReference lists
        stage_outputs = {}
        for stage_id, outputs_dicts in data.get("stageOutputs", {}).items():
            stage_outputs[stage_id] = [
                ArtifactReference.from_dict(output_dict)
                for output_dict in outputs_dicts
            ]
        
        return cls(
            workflow_id=data["workflowId"],
            manifest_version=data["manifestVersion"],
            name=data["name"],
            description=data.get("description"),
            parameters=data.get("parameters", {}),
            completed_stages=data.get("completedStages", []),
            failed_stage=data.get("failedStage"),
            stage_outputs=stage_outputs,
            stage_attempts=data.get("stageAttempts", {}),
            started_at=datetime.fromisoformat(data["startedAt"]) if data.get("startedAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"]) if data.get("updatedAt") else None,
            status=data.get("status", "pending")
        )