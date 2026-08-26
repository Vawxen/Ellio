# src/orchestrator/decision_log.py
"""
Decision log manager for audit trail.
"""

from typing import List, Optional
from datetime import datetime
from ..models.decision_log_entry import DecisionLogEntry
from ..models.artifact_reference import ArtifactReference
from ..utils.storage import storage


class DecisionLogManagerError(Exception):
    """Base exception for decision log manager errors."""
    pass


class DecisionLogManager:
    """
    Manages decision log entries for audit trail.
    """
    
    def __init__(self):
        """Initialize decision log manager."""
        self.storage = storage
    
    def log_quality_gate_decision(self, workflow_id: str, stage_id: str,
                                 decision: str, rationale: str,
                                 related_artifacts: List[ArtifactReference],
                                 metadata: Optional[dict] = None) -> str:
        """
        Log a quality gate decision to the decision log.
        
        Args:
            workflow_id: ID of the workflow
            stage_id: ID of the stage the decision relates to
            decision: Decision outcome (approved, rejected, etc.)
            rationale: Explanation for the decision
            related_artifacts: Artifacts related to this decision
            metadata: Optional additional metadata
            
        Returns:
            Entry ID of the logged decision
            
        Raises:
            DecisionLogManagerError: If decision cannot be logged
        """
        try:
            entry = DecisionLogEntry(
                timestamp=datetime.utcnow(),
                stage_id=stage_id,
                decision=decision,
                rationale=rationale,
                related_artifacts=related_artifacts,
                metadata=metadata or {}
            )
            
            entry_id = self.storage.append_decision_log_entry(workflow_id, entry)
            return entry_id
        except Exception as e:
            raise DecisionLogManagerError(f"Failed to log quality gate decision: {e}")
    
    def log_stage_transition(self, workflow_id: str, from_stage: str,
                           to_stage: str, decision: str, rationale: str,
                           related_artifacts: List[ArtifactReference],
                           metadata: Optional[dict] = None) -> str:
        """
        Log a stage transition to the decision log.
        
        Args:
            workflow_id: ID of the workflow
            from_stage: ID of the stage being transitioned from
            to_stage: ID of the stage being transitioned to
            decision: Transition decision (usually "approved")
            rationale: Explanation for the transition
            related_artifacts: Artifacts related to this transition
            metadata: Optional additional metadata
            
        Returns:
            Entry ID of the logged transition
            
        Raises:
            DecisionLogManagerError: If transition cannot be logged
        """
        try:
            # Enhance rationale with transition information
            enhanced_rationale = f"Transition from {from_stage} to {to_stage}: {rationale}"
            
            entry = DecisionLogEntry(
                timestamp=datetime.utcnow(),
                stage_id=to_stage,  # Logged against the target stage
                decision=decision,
                rationale=enhanced_rationale,
                related_artifacts=related_artifacts,
                metadata={
                    "transition_type": "stage_transition",
                    "from_stage": from_stage,
                    "to_stage": to_stage,
                    **(metadata or {})
                }
            )
            
            entry_id = self.storage.append_decision_log_entry(workflow_id, entry)
            return entry_id
        except Exception as e:
            raise DecisionLogManagerError(f"Failed to log stage transition: {e}")
    
    def log_workflow_event(self, workflow_id: str, event_type: str,
                         description: str, related_artifacts: List[ArtifactReference],
                         metadata: Optional[dict] = None) -> str:
        """
        Log a workflow event to the decision log.
        
        Args:
            workflow_id: ID of the workflow
            event_type: Type of event (started, completed, failed, etc.)
            description: Description of the event
            related_artifacts: Artifacts related to this event
            metadata: Optional additional metadata
            
        Returns:
            Entry ID of the logged event
            
        Raises:
            DecisionLogManagerError: If event cannot be logged
        """
        try:
            entry = DecisionLogEntry(
                timestamp=datetime.utcnow(),
                stage_id="workflow",  # Special stage ID for workflow-level events
                decision=event_type,
                rationale=description,
                related_artifacts=related_artifacts,
                metadata={
                    "event_type": event_type,
                    **(metadata or {})
                }
            )
            
            entry_id = self.storage.append_decision_log_entry(workflow_id, entry)
            return entry_id
        except Exception as e:
            raise DecisionLogManagerError(f"Failed to log workflow event: {e}")
    
    def get_decision_log_entries(self, workflow_id: str,
                               limit: Optional[int] = None) -> List[DecisionLogEntry]:
        """
        Get decision log entries for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            limit: Optional maximum number of entries to return (most recent first)
            
        Returns:
            List of DecisionLogEntry instances
            
        Raises:
            DecisionLogManagerError: If decision log cannot be loaded
        """
        try:
            return self.storage.load_decision_log_entries(workflow_id, limit)
        except Exception as e:
            raise DecisionLogManagerError(f"Failed to load decision log entries for workflow {workflow_id}: {e}")
    
    def get_decision_log_entry_count(self, workflow_id: str) -> int:
        """
        Get the number of decision log entries for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Number of decision log entries
        """
        try:
            return self.storage.get_decision_log_entry_count(workflow_id)
        except Exception:
            return 0
    
    def get_decision_log_reference(self, workflow_id: str) -> dict:
        """
        Get a reference to the decision log for checkpointing.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary with logId and entryCount for checkpoint reference
        """
        entry_count = self.get_decision_log_entry_count(workflow_id)
        # In this implementation, the workflow ID serves as the log ID
        return {
            "logId": workflow_id,
            "entryCount": entry_count
        }