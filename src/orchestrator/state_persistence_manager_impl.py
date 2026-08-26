# src/orchestrator/state_persistence_manager_impl.py
"""
Implementation of IStatePersistenceManager using existing checkpoint and resume logic.
"""
from typing import Optional
from ..models.checkpoint import Checkpoint
from ..models.workflow_state import WorkflowState
from ..models.parameterized_manifest import ParameterizedManifest
from .checkpoint_manager import CheckpointManager
from .decision_log import DecisionLogManager
from .state_persistence_manager import IStatePersistenceManager


class StatePersistenceManagerImpl(IStatePersistenceManager):
    """
    Manages workflow state loading, saving, and initialization.
    Delegates to CheckpointManager and uses ResumeHandler-like logic.
    """

    def __init__(self):
        """Initialize state persistence manager."""
        self.checkpoint_manager = CheckpointManager()
        self.decision_log_manager = DecisionLogManager()
        # Configuration values
        self.config = None  # We'll set this later or get from utils.config
        # For now, we'll import config inside methods if needed
        from ..utils.config import config as global_config
        self.config = global_config

    def load_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Load a workflow state by ID from the latest checkpoint.

        Args:
            workflow_id: The ID of the workflow to load.

        Returns:
            The loaded WorkflowState, or None if not found or cannot be loaded.
        """
        try:
            latest_checkpoint = self.checkpoint_manager.load_latest_checkpoint(workflow_id)
            if latest_checkpoint is None:
                return None
            return latest_checkpoint.state
        except Exception:
            # If any error occurs, return None to indicate inability to load
            return None

    def save_workflow_state(self, workflow_state: WorkflowState) -> None:
        """
        Save a workflow state by creating a checkpoint.

        Args:
            workflow_state: The workflow state to save.
        """
        try:
            # We need a decision log reference to create a checkpoint.
            # In the original code, the decision log reference is obtained from the decision log manager.
            decision_log_reference = self.decision_log_manager.get_decision_log_reference(
                workflow_state.workflow_id
            )
            # However, the CheckpointManager.create_checkpoint expects a dict for decision_log_reference.
            # The decision_log_manager.get_decision_log_reference returns a dict? Let's check.
            # We'll assume it returns a dict with logId and entryCount.
            # If not, we may need to adapt.
            # For now, we'll create a minimal reference.
            # Actually, looking at the decision_log.py, we see:
            #   def get_decision_log_reference(self, workflow_id: str) -> dict:
            #       return {"logId": workflow_id, "entryCount": self.get_decision_log_entry_count(workflow_id)}
            # So it returns a dict.
            self.checkpoint_manager.create_checkpoint(
                workflow_state=workflow_state,
                current_step="",  # We don't have the current step here; maybe we should pass it?
                decision_log_reference=decision_log_reference
            )
        except Exception:
            # In the original code, checkpoint failures are caught and ignored.
            # We'll do the same.
            pass

    def initialize_state(self, manifest: ParameterizedManifest) -> WorkflowState:
        """
        Create an initial workflow state from a manifest.

        Args:
            manifest: The parameterized manifest to initialize from.

        Returns:
            The initial WorkflowState.
        """
        # This is extracted from WorkflowExecutor._create_initial_workflow_state
        return WorkflowState(
            workflow_id=manifest.workflow_id,
            manifest_version=manifest.manifest_version,
            name=manifest.name,
            description=manifest.description,
            parameters=manifest.parameters.copy()
        )