# src/orchestrator/handoff_recorder.py
"""
Handoff recorder for documenting artifact transfers between stages.
"""

from typing import List, Dict, Any, Optional
from ..models.artifact_reference import ArtifactReference
from ..utils.storage import storage
import datetime
import uuid


class HandoffRecorderError(Exception):
    """Base exception for handoff recorder errors."""
    pass


class HandoffRecorder:
    """
    Records handoffs of artifacts between pipeline stages.
    """
    
    def __init__(self):
        """Initialize handoff recorder."""
        self.storage = storage
    
    def record_handoff(self, workflow_id: str, from_stage: str, to_stage: str,
                      artifacts: List[ArtifactReference],
                      decision: Dict[str, Any]) -> str:
        """
        Record a handoff of artifacts from one stage to another.
        
        Args.
            workflow_id: ID of the workflow
            from_stage: ID of the stage producing the artifacts
            to_stage: ID of the stage consuming the artifacts
            artifacts: List of artifact references being handed off
            decision: Quality gate decision that authorized this handoff
            
        Returns:
            Handoff ID of the recorded handoff
            
        Raises:
            HandoffRecorderError: If handoff cannot be recorded
        """
        try:
            # Generate handoff ID
            handoff_id = str(uuid.uuid4())
            
            # Create handoff record
            handoff_record = {
                "handoffId": handoff_id,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "fromStage": from_stage,
                "toStage": to_stage,
                "workflowId": workflow_id,
                "artifacts": [artifact.to_dict() for artifact in artifacts],
                "decision": decision,
                "version": "1.0.0"
            }
            
            # Validate handoff record
            self._validate_handoff_record(handoff_record)
            
            # Save to storage
            self.storage.save_handoff(handoff_record)
            
            return handoff_id
        except Exception as e:
            raise HandoffRecorderError(f"Failed to record handoff: {e}")
    
    def record_stage_output_handoff(self, workflow_id: str, stage_id: str,
                                  artifacts: List[ArtifactReference],
                                  quality_gate_decision: Dict[str, Any]) -> str:
        """
        Record a handoff of stage outputs to downstream stages.
        
        Args:
            workflow_id: ID of the workflow
            stage_id: ID of the stage producing the outputs
            artifacts: List of artifact references produced by the stage
            quality_gate_decision: Decision from quality gate that authorized outputs
            
        Returns:
            Handoff ID of the recorded handoff
            
        Raises:
            HandoffRecorderError: If handoff cannot be recorded
        """
        # In a more sophisticated implementation, we would determine which specific
        # downstream stages consume each artifact. For MVP, we'll create a general
        # handoff record that indicates the artifacts are available for consumption.
        
        # We'll use a special to_stage value to indicate these are available outputs
        # A real implementation would track actual consumer stages
        return self.record_handoff(
            workflow_id=workflow_id,
            from_stage=stage_id,
            to_stage="__AVAILABLE_OUTPUTS__",  # Special value indicating outputs are ready
            artifacts=artifacts,
            decision=quality_gate_decision
        )
    
    def get_handoff(self, handoff_id: str) -> Dict[str, Any]:
        """
        Get a handoff record by ID.
        
        Args:
            handoff_id: ID of the handoff to retrieve
            
        Returns:
            Handoff record dictionary
            
        Raises:
            HandoffRecorderError: If handoff cannot be retrieved
        """
        try:
            return self.storage.load_handoff(handoff_id)
        except Exception as e:
            raise HandoffRecorderError(f"Failed to load handoff {handoff_id}: {e}")
    
    def get_handoffs_for_workflow(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get all handoff records for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            List of handoff record dictionaries
        """
        try:
            handoff_ids = self.storage.list_handoffs(workflow_id=workflow_id)
            handoffs = []
            for handoff_id in handoff_ids:
                try:
                    handoff = self.storage.load_handoff(handoff_id)
                    handoffs.append(handoff)
                except Exception:
                    # Skip corrupted handoff records
                    continue
            return handoffs
        except Exception:
            return []
    
    def get_handoffs_from_stage(self, workflow_id: str, stage_id: str) -> List[Dict[str, Any]]:
        """
        Get all handoff records originating from a specific stage.
        
        Args:
            workflow_id: ID of the workflow
            stage_id: ID of the source stage
            
        Returns:
            List of handoff record dictionaries
        """
        try:
            handoff_ids = self.storage.list_handoffs(
                workflow_id=workflow_id,
                from_stage=stage_id
            )
            handoffs = []
            for handoff_id in handoff_ids:
                try:
                    handoff = self.storage.load_handoff(handoff_id)
                    handoffs.append(handoff)
                except Exception:
                    # Skip corrupted handoff records
                    continue
            return handoffs
        except Exception:
            return []
    
    def get_handoffs_to_stage(self, workflow_id: str, stage_id: str) -> List[Dict[str, Any]]:
        """
        Get all handoff records destined for a specific stage.
        
        Args:
            workflow_id: ID of the workflow
            stage_id: ID of the destination stage
            
        Returns:
            List of handoff record dictionaries
        """
        try:
            handoff_ids = self.storage.list_handoffs(
                workflow_id=workflow_id,
                to_stage=stage_id
            )
            handoffs = []
            for handoff_id in handoff_ids:
                try:
                    handoff = self.storage.load_handoff(handoff_id)
                    handoffs.append(handoff)
                except Exception:
                    # Skip corrupted handoff records
                    continue
            return handoffs
        except Exception:
            return []
    
    def _validate_handoff_record(self, handoff: Dict[str, Any]) -> None:
        """
        Validate a handoff record for correctness.
        
        Args:
            handoff: Handoff record dictionary to validate
            
        Raises:
            HandoffRecorderError: If handoff record is invalid
        """
        # Check required fields
        required_fields = ["handoffId", "timestamp", "fromStage", "toStage", 
                          "workflowId", "artifacts", "decision", "version"]
        for field in required_fields:
            if field not in handoff:
                raise HandoffRecorderError(f"Missing required field: {field}")
        
        # Validate field types
        if not isinstance(handoff["handoffId"], str) or not handoff["handoffId"].strip():
            raise HandoffRecorderError("handoffId must be a non-empty string")
        
        if not isinstance(handoff["timestamp"], str):
            raise HandoffRecorderError("timestamp must be a string")
        
        if not isinstance(handoff["fromStage"], str) or not handoff["fromStage"].strip():
            raise HandoffRecorderError("fromStage must be a non-empty string")
        
        if not isinstance(handoff["toStage"], str) or not handoff["toStage"].strip():
            raise HandoffRecorderError("toStage must be a non-empty string")
        
        if not isinstance(handoff["workflowId"], str) or not handoff["workflowId"].strip():
            raise HandoffRecorderError("workflowId must be a non-empty string")
        
        if not isinstance(handoff["artifacts"], list):
            raise HandoffRecorderError("artifacts must be a list")
        
        for i, artifact in enumerate(handoff["artifacts"]):
            if not isinstance(artifact, dict):
                raise HandoffRecorderError(f"artifacts[{i}] must be a dictionary")
            # Validate it's a valid artifact reference
            ArtifactReference.from_dict(artifact)  # Will raise if invalid
        
        if not isinstance(handoff["decision"], dict):
            raise HandoffRecorderError("decision must be a dictionary")
        if "decision" not in handoff["decision"] or "rationale" not in handoff["decision"]:
            raise HandoffRecorderError("decision must have 'decision' and 'rationale' fields")
        
        if not isinstance(handoff["version"], str):
            raise HandoffRecorderError("version must be a string")