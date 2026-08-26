# src/models/parameterized_manifest.py
"""
Parameterized manifest model for the orchestration spine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .stage_definition import StageDefinition
from .artifact_reference import ArtifactReference


@dataclass
class ParameterizedManifest:
    """
    A manifest with parameters applied, ready for execution.
    """
    manifest_version: str
    workflow_id: str
    name: str
    description: Optional[str] = None
    stages: List[StageDefinition] = field(default_factory=list)
    global_quality_gates: List[Dict[str, Any]] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.manifest_version:
            raise ValueError("manifest_version cannot be empty")
        if not self.workflow_id:
            raise ValueError("workflow_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        
        # Validate stages
        if not isinstance(self.stages, list):
            raise ValueError("stages must be a list")
        for stage in self.stages:
            if not isinstance(stage, StageDefinition):
                raise ValueError("stages items must be StageDefinition instances")
        
        # Validate global_quality_gates
        if not isinstance(self.global_quality_gates, list):
            raise ValueError("global_quality_gates must be a list")
        for gate in self.global_quality_gates:
            if not isinstance(gate, dict):
                raise ValueError("global_quality_gates items must be dictionaries")
            if "gateId" not in gate or "type" not in gate:
                raise ValueError("global_quality_gates items must have 'gateId' and 'type' fields")

    def get_stage_by_id(self, stage_id: str) -> Optional[StageDefinition]:
        """
        Get a stage definition by its ID.
        
        Args:
            stage_id: ID of the stage to find
            
        Returns:
            StageDefinition if found, None otherwise
        """
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def get_stages_ready_for_execution(self, completed_stages: List[str]) -> List[StageDefinition]:
        """
        Get stages whose dependencies are satisfied.
        
        Args.
            completed_stages: List of stage IDs that have completed successfully
            
        Returns:
            List of StageDefinition instances that are ready to execute
        """
        ready_stages = []
        for stage in self.stages:
            if stage.is_ready(completed_stages):
                ready_stages.append(stage)
        return ready_stages

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the parameterized manifest
        """
        return {
            "manifestVersion": self.manifest_version,
            "workflowId": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "stages": [stage.to_dict() for stage in self.stages],
            "globalQualityGates": self.global_quality_gates,
            "parameters": self.parameters
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ParameterizedManifest':
        """
        Create ParameterizedManifest from dictionary.
        
        Args:
            data: Dictionary with parameterized manifest data
            
        Returns:
            ParameterizedManifest instance
        """
        return cls(
            manifest_version=data["manifestVersion"],
            workflow_id=data["workflowId"],
            name=data["name"],
            description=data.get("description"),
            stages=[
                StageDefinition.from_dict(stage_data)
                for stage_data in data.get("stages", [])
            ],
            global_quality_gates=data.get("globalQualityGates", []),
            parameters=data.get("parameters", {})
        )