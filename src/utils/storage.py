# src/utils/storage.py
"""
Storage abstraction layer for the orchestration spine.
MVP implementation uses local filesystem.
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from ..models.checkpoint import Checkpoint
from ..models.decision_log_entry import DecisionLogEntry
from ..models.artifact_reference import ArtifactReference
from ..utils.config import config


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class Storage:
    """
    Storage abstraction for checkpoints, handoffs, and decision logs.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage with base path.
        
        Args:
            base_path: Base directory for storage (uses config if not provided)
        """
        self.base_path = Path(base_path) if base_path else Path(config.get("checkpoint_storage_path", "./storage"))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Define storage subdirectories
        self.checkpoints_path = self.base_path / "checkpoints"
        self.handoffs_path = self.base_path / "handoffs"
        self.decision_logs_path = self.base_path / "decision_logs"
        
        # Create subdirectories
        self.checkpoints_path.mkdir(parents=True, exist_ok=True)
        self.handoffs_path.mkdir(parents=True, exist_ok=True)
        self.decision_logs_path.mkdir(parents=True, exist_ok=True)
    
    # Checkpoint storage methods
    def save_checkpoint(self, checkpoint: Checkpoint) -> str:
        """
        Save a checkpoint to storage.
        
        Args:
            checkpoint: Checkpoint to save
            
        Returns:
            ID of the saved checkpoint
            
        Raises:
            StorageError: If checkpoint cannot be saved
        """
        try:
            # Generate checkpoint ID if not provided
            if not checkpoint.checkpoint_id:
                checkpoint.checkpoint_id = str(uuid.uuid4())
            
            # Ensure timestamp is set
            if not checkpoint.timestamp:
                checkpoint.timestamp = datetime.utcnow()
            
            # Create file path
            file_path = self.checkpoints_path / f"{checkpoint.checkpoint_id}.json"
            
            # Write checkpoint to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.to_dict(), f, indent=2, default=str)
            
            return checkpoint.checkpoint_id
        except Exception as e:
            raise StorageError(f"Failed to save checkpoint: {e}")
    
    def load_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        """
        Load a checkpoint from storage.
        
        Args:
            checkpoint_id: ID of the checkpoint to load
            
        Returns:
            Loaded Checkpoint instance
            
        Raises:
            StorageError: If checkpoint cannot be loaded or not found
        """
        try:
            file_path = self.checkpoints_path / f"{checkpoint_id}.json"
            if not file_path.exists():
                raise StorageError(f"Checkpoint not found: {checkpoint_id}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Checkpoint.from_dict(data)
        except Exception as e:
            raise StorageError(f"Failed to load checkpoint {checkpoint_id}: {e}")
    
    def list_checkpoints(self, workflow_id: Optional[str] = None) -> List[str]:
        """
        List available checkpoint IDs.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            List of checkpoint IDs
        """
        checkpoint_ids = []
        for file_path in self.checkpoints_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if workflow_id is None or data.get("workflowId") == workflow_id:
                    checkpoint_ids.append(data["checkpointId"])
            except Exception:
                # Skip corrupted checkpoint files
                continue
        return sorted(checkpoint_ids)
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint from storage.
        
        Args:
            checkpoint_id: ID of the checkpoint to delete
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.checkpoints_path / f"{checkpoint_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    # Handoff storage methods
    def save_handoff(self, handoff: Dict[str, Any]) -> str:
        """
        Save a handoff record to storage.
        
        Args:
            handoff: Handoff record dictionary to save
            
        Returns:
            ID of the saved handoff
            
        Raises:
            StorageError: If handoff cannot be saved
        """
        try:
            # Generate handoff ID if not provided
            handoff_id = handoff.get("handoffId", str(uuid.uuid4()))
            handoff["handoffId"] = handoff_id
            
            # Ensure timestamp is set
            if "timestamp" not in handoff or not handoff["timestamp"]:
                handoff["timestamp"] = datetime.utcnow().isoformat()
            
            # Create file path
            file_path = self.handoffs_path / f"{handoff_id}.json"
            
            # Write handoff to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(handoff, f, indent=2, default=str)
            
            return handoff_id
        except Exception as e:
            raise StorageError(f"Failed to save handoff: {e}")
    
    def load_handoff(self, handoff_id: str) -> Dict[str, Any]:
        """
        Load a handoff record from storage.
        
        Args:
            handoff_id: ID of the handoff to load
            
        Returns:
            Handoff record dictionary
            
        Raises:
            StorageError: If handoff cannot be loaded or not found
        """
        try:
            file_path = self.handoffs_path / f"{handoff_id}.json"
            if not file_path.exists():
                raise StorageError(f"Handoff not found: {handoff_id}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load handoff {handoff_id}: {e}")
    
    def list_handoffs(self, workflow_id: Optional[str] = None, 
                     from_stage: Optional[str] = None,
                     to_stage: Optional[str] = None) -> List[str]:
        """
        List available handoff IDs with optional filtering.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            from_stage: Optional fromStage to filter by
            to_stage: Optional toStage to filter by
            
        Returns:
            List of handoff IDs
        """
        handoff_ids = []
        for file_path in self.handoffs_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Apply filters
                if workflow_id is not None and data.get("workflowId") != workflow_id:
                    continue
                if from_stage is not None and data.get("fromStage") != from_stage:
                    continue
                if to_stage is not None and data.get("toStage") != to_stage:
                    continue
                
                handoff_ids.append(data["handoffId"])
            except Exception:
                # Skip corrupted handoff files
                continue
        return sorted(handoff_ids)
    
    # Decision log storage methods
    def append_decision_log_entry(self, workflow_id: str, entry: DecisionLogEntry) -> str:
        """
        Append a decision log entry to the workflow's decision log.
        
        Args:
            workflow_id: ID of the workflow
            entry: Decision log entry to append
            
        Returns:
            ID of the decision log entry (based on timestamp and workflow ID)
            
        Raises:
            StorageError: If entry cannot be appended
        """
        try:
            # Create workflow-specific decision log file
            log_file = self.decision_logs_path / f"{workflow_id}.jsonl"
            
            # Append entry as JSON line
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict(), default=str) + "\n")
            
            # Generate entry ID based on timestamp and workflow ID
            entry_id = f"{workflow_id}_{entry.timestamp.timestamp()}"
            return entry_id
        except Exception as e:
            raise StorageError(f"Failed to append decision log entry: {e}")
    
    def load_decision_log_entries(self, workflow_id: str, 
                                 limit: Optional[int] = None) -> List[DecisionLogEntry]:
        """
        Load decision log entries for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            limit: Optional maximum number of entries to return (most recent first)
            
        Returns:
            List of DecisionLogEntry instances
            
        Raises:
            StorageError: If decision log cannot be loaded
        """
        try:
            log_file = self.decision_logs_path / f"{workflow_id}.jsonl"
            if not log_file.exists():
                return []
            
            entries = []
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            entries.append(DecisionLogEntry.from_dict(data))
                        except Exception:
                            # Skip corrupted lines
                            continue
            
            # Sort by timestamp (oldest first) and apply limit
            entries.sort(key=lambda x: x.timestamp)
            if limit is not None:
                entries = entries[-limit:]  # Get most recent entries
            
            return entries
        except Exception as e:
            raise StorageError(f"Failed to load decision log entries for workflow {workflow_id}: {e}")
    
    def get_decision_log_entry_count(self, workflow_id: str) -> int:
        """
        Get the number of decision log entries for a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Number of decision log entries
        """
        try:
            log_file = self.decision_logs_path / f"{workflow_id}.jsonl"
            if not log_file.exists():
                return 0
            
            count = 0
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        count += 1
            return count
        except Exception:
            return 0


# Global storage instance
storage = Storage()