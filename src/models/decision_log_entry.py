# src/models/decision_log_entry.py
"""
Decision log entry model for audit trail.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .artifact_reference import ArtifactReference


@dataclass(frozen=True)
class DecisionLogEntry:
    """
    Immutable entry in the decision log for audit trail.
    """
    timestamp: datetime
    stage_id: str
    decision: str  # approved, rejected, needs_revision, etc.
    rationale: str
    related_artifacts: List[ArtifactReference] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime instance")
        if not self.stage_id:
            raise ValueError("stage_id cannot be empty")
        if not self.decision:
            raise ValueError("decision cannot be empty")
        if not self.rationale:
            raise ValueError("rationale cannot be empty")
        if not isinstance(self.related_artifacts, list):
            raise ValueError("related_artifacts must be a list")
        for artifact in self.related_artifacts:
            if not isinstance(artifact, ArtifactReference):
                raise ValueError("related_artifacts items must be ArtifactReference instances")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the decision log entry
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "stageId": self.stage_id,
            "decision": self.decision,
            "rationale": self.rationale,
            "relatedArtifacts": [artifact.to_dict() for artifact in self.related_artifacts],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DecisionLogEntry':
        """
        Create DecisionLogEntry from dictionary.
        
        Args:
            data: Dictionary with decision log entry data
            
        Returns:
            DecisionLogEntry instance
        """
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            stage_id=data["stageId"],
            decision=data["decision"],
            rationale=data["rationale"],
            related_artifacts=[
                ArtifactReference.from_dict(artifact_dict)
                for artifact_dict in data.get("relatedArtifacts", [])
            ],
            metadata=data.get("metadata", {})
        )