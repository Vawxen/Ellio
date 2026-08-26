# src/orchestrator/execution_validation_manager_impl.py
"""
Implementation of IExecutionValidationManager using existing stage runner and quality gate logic.
"""
from typing import List, Dict, Any, Optional
from ..models.parameterized_manifest import ParameterizedManifest
from ..models.stage_execution_result import StageExecutionResult
from ..models.artifact_reference import ArtifactReference
from ..models.workflow_state import WorkflowState
from .stage_runner import StageRunner
from .quality_gate import QualityGateEngine
from .execution_validation_manager import IExecutionValidationManager


class ExecutionValidationManagerImpl(IExecutionValidationManager):
    """
    Executes stages and validates their outputs.
    Delegates to StageRunner for execution and QualityGateEngine for validation.
    """

    def __init__(self):
        """Initialize execution and validation manager."""
        self.stage_runner = StageRunner()
        self.quality_gate_engine = QualityGateEngine()

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
        # Note: The WorkflowExecutor should have already incremented the attempt counter
        # and resolved the input artifacts. We just execute the stage.
        stage_result = self.stage_runner.run_stage(
            stage_def.to_dict(),
            input_artifacts,
            manifest.parameters
        )
        return stage_result

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
        # Get quality gates for this stage
        quality_gates = stage_def.quality_gates
        
        # Also consider global quality gates
        global_gates = manifest.global_quality_gates
        all_gates = quality_gates + global_gates
        
        # If no quality gates defined, auto-approve
        if not all_gates:
            return {
                "decision": "approved",
                "rationale": "No quality gates defined for this stage",
                "relatedArtifacts": artifacts
            }
        
        # Validate each artifact with each quality gate
        # For simplicity, we'll require all artifacts to pass all gates
        all_validation_results = []
        
        for artifact in artifacts:
            for gate in all_gates:
                gate_type = gate.get("type", "schemaValidation")
                gate_config = gate.get("config", {})
                
                try:
                    validation_result = self.quality_gate_engine.validate_artifact(
                        artifact=artifact,
                        gate_config={**gate, "config": gate_config} if gate_config else gate
                    )
                    all_validation_results.append(validation_result)
                except Exception as e:
                    # If validation fails completely, create a failed validation result
                    from ..models.validation_result import ValidationResult
                    failed_result = ValidationResult(
                        is_valid=False,
                        validated_at=datetime.datetime.utcnow(),
                        artifact_reference=artifact
                    )
                    failed_result.add_error(
                        "VALIDATION_ERROR",
                        f"Quality gate validation failed: {e}",
                        artifact_reference=artifact
                    )
                    all_validation_results.append(failed_result)
        
        # Make overall decision based on all validation results
        # For MVP, we'll use the first failed validation's decision, or approve if all passed
        any_failed = any(not result.is_valid for result in all_validation_results)
        
        if any_failed:
            # Find the first failed validation to use for decision
            failed_result = next((r for r in all_validation_results if not r.is_valid), all_validation_results[0])
            decision = self.quality_gate_engine.make_quality_gate_decision(failed_result)
        else:
            # All validations passed
            # Use the first validation result to create an approved decision
            if all_validation_results:
                decision = self.quality_gate_engine.make_quality_gate_decision(all_validation_results[0])
            else:
                # No artifacts to validate
                decision = {
                    "decision": "approved",
                    "rationale": "No artifacts to validate",
                    "relatedArtifacts": []
                }
        
        return decision