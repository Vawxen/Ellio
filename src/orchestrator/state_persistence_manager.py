# src/orchestrator/state_persistence_manager.py
"""
Interface for state persistence management.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..models.workflow_state import WorkflowState
from ..models.parameterized_manifest import ParameterizedManifest


class IStatePersistenceManager(ABC):
    """
    Manages workflow state loading, saving, and initialization.
    """

    @abstractmethod
    def load_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """
        Load a workflow state by ID.

        Args:
            workflow_id: The ID of the workflow to load.

        Returns:
            The loaded WorkflowState, or None if not found.
        """
        pass

    @abstractmethod
    def save_workflow_state(self, workflow_state: WorkflowState) -> None:
        """
        Save a workflow state.

        Args:
            workflow_state: The workflow state to save.
        """
        pass

    @abstractmethod
    def initialize_state(self, manifest: ParameterizedManifest) -> WorkflowState:
        """
        Create an initial workflow state from a manifest.

        Args:
            manifest: The parameterized manifest to initialize from.

        Returns:
            The initial WorkflowState.
        """
        pass