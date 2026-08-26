# src/models/stage_definition.py
"""
Stage definition model for the orchestration spine.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .artifact_reference import ArtifactReference


@dataclass
class StageDefinition:
    """
    Definition of a pipeline stage as specified in the manifest.
    """
    stage_id: str
    agent_role: str
    depends_on: List[str] = field(default_factory=list)
    inputs: List[ArtifactReference] = field(default_factory=list)
    outputs: List[ArtifactReference] = field(default_factory=list)
    quality_gates: List[Dict[str, Any]] = field(default_factory=list)
    timeout_seconds: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.stage_id:
            raise ValueError("stage_id cannot be empty")
        if not self.agent_role:
            raise ValueError("agent_role cannot be empty")
        
        # Validate depends_on
        if not isinstance(self.depends_on, list):
            raise ValueError("depends_on must be a list")
        for dep in self.depends_on:
            if not isinstance(dep, str):
                raise ValueError("depends_on items must be strings")
            if not dep:
                raise ValueError("depends_on items cannot be empty strings")
        
        # Validate inputs
        if not isinstance(self.inputs, list):
            raise ValueError("inputs must be a list")
        for inp in self.inputs:
            if not isinstance(inp, ArtifactReference):
                raise ValueError("inputs must be ArtifactReference instances")
        
        # Validate outputs
        if not isinstance(self.outputs, list):
            raise ValueError("outputs must be a list")
        for out in self.outputs:
            if not isinstance(out, ArtifactReference):
                raise ValueError("outputs must be ArtifactReference instances")
        
        # Validate quality_gates
        if not isinstance(self.quality_gates, list):
            raise ValueError("quality_gates must be a list")
        for gate in self.quality_gates:
            if not isinstance(gate, dict):
                raise ValueError("quality_gates items must be dictionaries")
            if "gateId" not in gate or "type" not in gate:
                raise ValueError("quality_gates items must have 'gateId' and 'type' fields")
        
        # Validate timeout_seconds
        if self.timeout_seconds is not None:
            if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1:
                raise ValueError("timeout_seconds must be a positive integer or None")
        
        # Validate retry_policy
        if self.retry_policy is not None:
            if not isinstance(self.retry_policy, dict):
                raise ValueError("retry_policy must be a dictionary or None")
            max_attempts = self.retry_policy.get("maxAttempts", 0)
            if not isinstance(max_attempts, int) or max_attempts < 0:
                raise ValueError("retry_policy.maxAttempts must be a non-negative integer")
            backoff = self.retry_policy.get("backoffSeconds", 0)
            if not isinstance(backoff, int) or backoff < 0:
                raise ValueError("retry_policy.backoffSeconds must be a non-negative integer")

    def is_ready(self, completed_stages: List[str]) -> bool:
        """
        Check if this stage's dependencies are satisfied.
        
        Args:
            completed_stages: List of stage IDs that have completed successfully
            
        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        return all(dep in completed_stages for dep in self.depends_on)

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the stage definition
        """
        return {
            "stageId": self.stage_id,
            "agentRole": self.agent_role,
            "dependsOn": self.depends_on,
            "inputs": [inp.to_dict() for inp in self.inputs],
            "outputs": [out.to_dict() for out in self.outputs],
            "qualityGates": self.quality_gates,
            "timeoutSeconds": self.timeout_seconds,
            "retryPolicy": self.retry_policy
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'StageDefinition':
        """
        Create StageDefinition from dictionary.
        
        Args:
            data: Dictionary with stage definition data
            
        Returns:
            StageDefinition instance
        """
        return cls(
            stage_id=data["stageId"],
            agent_role=data["agentRole"],
            depends_on=data.get("dependsOn", []),
            inputs=[
                ArtifactReference.from_dict(inp)
                for inp in data.get("inputs", [])
            ],
            outputs=[
                ArtifactReference.from_dict(out)
                for out in data.get("outputs", [])
            ],
            quality_gates=data.get("qualityGates", []),
            timeout_seconds=data.get("timeoutSeconds"),
            retry_policy=data.get("retryPolicy")
        )