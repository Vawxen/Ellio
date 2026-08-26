# src/models/artifact_reference.py
"""
Artifact reference model for the orchestration spine.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ArtifactReference:
    """
    Immutable reference to an artifact produced or consumed by pipeline stages.
    
    This follows the Artifact Reference Contract defined in the shared documentation.
    """
    artifact_type: str
    artifact_id: str
    version: str
    location: str
    producer_stage: str
    validation_status: str  # pending, passed, failed, skipped

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.artifact_type:
            raise ValueError("artifact_type cannot be empty")
        if not self.artifact_id:
            raise ValueError("artifact_id cannot be empty")
        if not self.version:
            raise ValueError("version cannot be empty")
        if not self.location:
            raise ValueError("location cannot be empty")
        # producer_stage can be empty for external artifacts
        if self.producer_stage is None:
            raise ValueError("producer_stage cannot be None")
        if self.validation_status not in ["pending", "passed", "failed", "skipped"]:
            raise ValueError(
                f"validation_status must be one of: pending, passed, failed, skipped. "
                f"Got: {self.validation_status}"
            )

    def with_updated_status(self, validation_status: str) -> 'ArtifactReference':
        """
        Create a new ArtifactReference with updated validation status.
        
        Args:
            validation_status: New validation status
            
        Returns:
            New ArtifactReference instance with updated status
        """
        if validation_status not in ["pending", "passed", "failed", "skipped"]:
            raise ValueError(
                f"validation_status must be one of: pending, passed, failed, skipped. "
                f"Got: {validation_status}"
            )
        
        return ArtifactReference(
            artifact_type=self.artifact_type,
            artifact_id=self.artifact_id,
            version=self.version,
            location=self.location,
            producer_stage=self.producer_stage,
            validation_status=validation_status
        )

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the artifact reference
        """
        return {
            "artifactType": self.artifact_type,
            "artifactId": self.artifact_id,
            "version": self.version,
            "location": self.location,
            "producerStage": self.producer_stage,
            "validationStatus": self.validation_status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ArtifactReference':
        """
        Create ArtifactReference from dictionary.
        
        Args:
            data: Dictionary with artifact reference data
            
        Returns:
            ArtifactReference instance
        """
        return cls(
            artifact_type=data["artifactType"],
            artifact_id=data["artifactId"],
            version=data["version"],
            location=data["location"],
            producer_stage=data["producerStage"],
            validation_status=data["validationStatus"]
        )