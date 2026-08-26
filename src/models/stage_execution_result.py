# src/models/stage_execution_result.py
"""
Stage execution result model for capturing stage execution outcomes.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from .artifact_reference import ArtifactReference


@dataclass
class StageExecutionResult:
    """
    Result of executing a pipeline stage.
    """
    stage_id: str
    started_at: datetime
    finished_at: datetime
    exit_code: int
    stdout: str
    stderr: str
    artifacts_produced: List[ArtifactReference] = field(default_factory=list)
    artifacts_used: List[ArtifactReference] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.stage_id:
            raise ValueError("stage_id cannot be empty")
        if not isinstance(self.started_at, datetime):
            raise ValueError("started_at must be a datetime instance")
        if not isinstance(self.finished_at, datetime):
            raise ValueError("finished_at must be a datetime instance")
        if self.finished_at < self.started_at:
            raise ValueError("finished_at must be after started_at")
        if not isinstance(self.exit_code, int):
            raise ValueError("exit_code must be an integer")
        if not isinstance(self.stdout, str):
            raise ValueError("stdout must be a string")
        if not isinstance(self.stderr, str):
            raise ValueError("stderr must be a string")
        if not isinstance(self.artifacts_produced, list):
            raise ValueError("artifacts_produced must be a list")
        for artifact in self.artifacts_produced:
            if not isinstance(artifact, ArtifactReference):
                raise ValueError("artifacts_produced items must be ArtifactReference instances")
        if not isinstance(self.artifacts_used, list):
            raise ValueError("artifacts_used must be a list")
        for artifact in self.artifacts_used:
            if not isinstance(artifact, ArtifactReference):
                raise ValueError("artifacts_used items must be ArtifactReference instances")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    @property
    def duration_seconds(self) -> float:
        """
        Get the duration of stage execution in seconds.
        
        Returns:
            Duration as a float
        """
        return (self.finished_at - self.started_at).total_seconds()

    @property
    def succeeded(self) -> bool:
        """
        Check if the stage execution succeeded (exit code 0).
        
        Returns:
            True if exit code is 0, False otherwise
        """
        return self.exit_code == 0

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the stage execution result
        """
        return {
            "stageId": self.stage_id,
            "startedAt": self.started_at.isoformat(),
            "finishedAt": self.finished_at.isoformat(),
            "exitCode": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "artifactsProduced": [artifact.to_dict() for artifact in self.artifacts_produced],
            "artifactsUsed": [artifact.to_dict() for artifact in self.artifacts_used],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StageExecutionResult':
        """
        Create StageExecutionResult from dictionary.
        
        Args:
            data: Dictionary with stage execution result data
            
        Returns:
            StageExecutionResult instance
        """
        return cls(
            stage_id=data["stageId"],
            started_at=datetime.fromisoformat(data["startedAt"]),
            finished_at=datetime.fromisoformat(data["finishedAt"]),
            exit_code=data["exitCode"],
            stdout=data["stdout"],
            stderr=data["stderr"],
            artifacts_produced=[
                ArtifactReference.from_dict(artifact_dict)
                for artifact_dict in data.get("artifactsProduced", [])
            ],
            artifacts_used=[
                ArtifactReference.from_dict(artifact_dict)
                for artifact_dict in data.get("artifactsUsed", [])
            ],
            metadata=data.get("metadata", {})
        )