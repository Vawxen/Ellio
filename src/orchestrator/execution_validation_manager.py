# src/orchestrator/execution_validation_manager.py
"""
Interface for execution and validation management.
"""
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.parameterized_manifest import ParameterizedManifest
from ..models.stage_execution_result import StageExecutionResult
from ..models.artifact_reference import ArtifactReference
from ..models.workflow_state import WorkflowState


class IExecutionValidationManager(ABC):
    """
    Executes stages and validates their outputs.
    """

    @abstractmethod
    def execute_stage(
        self,
        stage_def: 'StageDefinition',
        workflow_state: WorkflowState,
        manifest: ParameterizedManifest,
        input_artifacts: List[ArtifactReference]
    ) -> StageExecutionResult:
        """
        Execute a single stage.

        Args:
            stage_def: The stage definition to execute.
            workflow_state: The current workflow state.
            manifest: The workflow manifest.
            input_artifacts: The input artifacts for the stage.

        Returns:
            The result of the stage execution.
        """
        pass

    @abstractmethod
    def validate_stage_outputs(
        self,
        artifacts: List[ArtifactReference],
        stage_def: 'StageDefinition',
        manifest: ParameterizedManifest
    ) -> Dict[str, Any]:
        """
        Validate the outputs of a stage.

        Args:
            artifacts: The artifacts produced by the stage.
            stage_def: The stage definition.
            manifest: The workflow manifest.

        Returns:
            A dictionary representing the validation decision (with keys like 'decision', 'rationale', etc.).
        """
        pass