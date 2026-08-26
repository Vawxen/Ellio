# src/orchestrator/manifest.py
"""
Manifest parser and validator for the MVP orchestration spine.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from copy import deepcopy

from ..models import ArtifactReference, StageDefinition, ParameterizedManifest


class ManifestError(Exception):
    """Base exception for manifest-related errors."""
    pass


class ManifestValidationError(ManifestError):
    """Raised when manifest validation fails."""
    pass


class ManifestVersionError(ManifestError):
    """Raised when manifest version is incompatible."""
    pass


class ManifestParser:
    """
    Parses and validates orchestration manifests.
    
    Features:
    - JSON manifest parsing
    - Schema validation
    - Parameter substitution
    - Version compatibility checking
    """

    # Supported manifest versions
    SUPPORTED_VERSIONS = ["1.0.0"]
    LATEST_VERSION = "1.0.0"

    # JSON schema for manifest validation (simplified for MVP)
    MANIFEST_SCHEMA = {
        "type": "object",
        "required": ["manifestVersion", "workflowId", "name", "stages"],
        "properties": {
            "manifestVersion": {"type": "string"},
            "workflowId": {"type": "string"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "stages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["stageId", "agentRole"],
                    "properties": {
                        "stageId": {"type": "string"},
                        "agentRole": {"type": "string"},
                        "dependsOn": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
"inputs": {
                             "type": "array",
                             "items": {
                                 "type": "object",
                                 "required": ["artifactType", "artifactId", "version", "location"],
                                 "properties": {
                                     "artifactType": {"type": "string"},
                                     "artifactId": {"type": "string"},
                                     "version": {"type": "string"},
                                     "location": {"type": "string"}
                                 }
                             }
                         },
"outputs": {
                             "type": "array",
                             "items": {
                                 "type": "object",
                                 "required": ["artifactType", "artifactId", "version", "location"],
                                 "properties": {
                                     "artifactType": {"type": "string"},
                                     "artifactId": {"type": "string"},
                                     "version": {"type": "string"},
                                     "location": {"type": "string"}
                                 }
                             }
                         },
                        "qualityGates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["gateId", "type"],
                                "properties": {
                                    "gateId": {"type": "string"},
                                    "type": {"type": "string"},
                                    "config": {"type": "object"}
                                }
                            }
                        },
                        "timeoutSeconds": {"type": "integer", "minimum": 1},
                        "retryPolicy": {
                            "type": "object",
                            "properties": {
                                "maxAttempts": {"type": "integer", "minimum": 0},
                                "backoffSeconds": {"type": "integer", "minimum": 0}
                            }
                        }
                    }
                }
            },
            "globalQualityGates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["gateId", "type"],
                    "properties": {
                        "gateId": {"type": "string"},
                        "type": {"type": "string"},
                        "config": {"type": "object"}
                    }
                }
            }
        }
    }

    def __init__(self):
        self._manifest: Optional[Dict[str, Any]] = None
        self._parameters: Dict[str, Any] = {}

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse a manifest from a JSON file.
        
        Args:
            file_path: Path to the manifest JSON file
            
        Returns:
            Parsed manifest dictionary
            
        Raises:
            ManifestError: If file cannot be read or parsed
            ManifestValidationError: If manifest structure is invalid
            ManifestVersionError: If manifest version is unsupported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_manifest = json.load(f)
        except FileNotFoundError:
            raise ManifestError(f"Manifest file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ManifestError(f"Invalid JSON in manifest file: {e}")
        
        return self.parse(raw_manifest)

    def parse(self, raw_manifest: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse and validate a manifest from a dictionary or JSON string.
        
        Args:
            raw_manifest: Manifest as dictionary or JSON string
            
        Returns:
            Validated and processed manifest dictionary
            
        Raises:
            ManifestError: If manifest cannot be parsed
            ManifestValidationError: If manifest structure is invalid
            ManifestVersionError: If manifest version is unsupported
        """
        if isinstance(raw_manifest, str):
            try:
                raw_manifest = json.loads(raw_manifest)
            except json.JSONDecodeError as e:
                raise ManifestError(f"Invalid JSON manifest: {e}")
        
        if not isinstance(raw_manifest, dict):
            raise ManifestError("Manifest must be a dictionary or JSON string")
        
        # Store raw manifest for parameter substitution
        self._manifest = deepcopy(raw_manifest)
        
        # Validate manifest structure
        self._validate_structure(self._manifest)
        
        # Validate version
        self._validate_version(self._manifest.get("manifestVersion"))
        
        # Apply parameter substitution if parameters are set
        if self._parameters:
            self._manifest = self._substitute_parameters(self._manifest, self._parameters)
        
        return self._manifest

    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Set parameters for substitution in the manifest.
        
        Args:
            parameters: Dictionary of parameter names to values
        """
        self._parameters = parameters

    def _validate_structure(self, manifest: Dict[str, Any]) -> None:
        """
        Validate manifest structure against the schema.
        
        Args:
            manifest: Manifest dictionary to validate
            
        Raises:
            ManifestValidationError: If validation fails
        """
        # Check required top-level fields
        for field in ["manifestVersion", "workflowId", "name", "stages"]:
            if field not in manifest:
                raise ManifestValidationError(f"Missing required field: {field}")
        
        # Validate manifestVersion is string
        if not isinstance(manifest.get("manifestVersion"), str):
            raise ManifestValidationError("manifestVersion must be a string")
        
        # Validate workflowId is string
        if not isinstance(manifest.get("workflowId"), str):
            raise ManifestValidationError("workflowId must be a string")
        
        # Validate name is string
        if not isinstance(manifest.get("name"), str):
            raise ManifestValidationError("name must be a string")
        
        # Validate stages is array
        stages = manifest.get("stages")
        if not isinstance(stages, list):
            raise ManifestValidationError("stages must be an array")
        
        # Validate each stage
        for i, stage in enumerate(stages):
            self._validate_stage(stage, i)
        
        # Validate globalQualityGates if present
        global_gates = manifest.get("globalQualityGates", [])
        if not isinstance(global_gates, list):
            raise ManifestValidationError("globalQualityGates must be an array")
        
        for i, gate in enumerate(global_gates):
            self._validate_quality_gate(gate, f"globalQualityGates[{i}]")

    def _validate_stage(self, stage: Dict[str, Any], index: int) -> None:
        """
        Validate a single stage definition.
        
        Args:
            stage: Stage dictionary to validate
            index: Index of stage in stages array (for error reporting)
            
        Raises:
            ManifestValidationError: If stage validation fails
        """
        prefix = f"stages[{index}]"
        
        # Check required fields
        if "stageId" not in stage:
            raise ManifestValidationError(f"{prefix}: missing required field 'stageId'")
        if "agentRole" not in stage:
            raise ManifestValidationError(f"{prefix}: missing required field 'agentRole'")
        
        # Validate field types
        if not isinstance(stage.get("stageId"), str):
            raise ManifestValidationError(f"{prefix}: stageId must be a string")
        if not isinstance(stage.get("agentRole"), str):
            raise ManifestValidationError(f"{prefix}: agentRole must be a string")
        
        # Validate dependsOn if present
        depends_on = stage.get("dependsOn", [])
        if not isinstance(depends_on, list):
            raise ManifestValidationError(f"{prefix}: dependsOn must be an array")
        for dep in depends_on:
            if not isinstance(dep, str):
                raise ManifestValidationError(f"{prefix}: dependsOn items must be strings")
        
        # Validate inputs if present
        inputs = stage.get("inputs", [])
        if not isinstance(inputs, list):
            raise ManifestValidationError(f"{prefix}: inputs must be an array")
        for i, inp in enumerate(inputs):
            self._validate_artifact_reference(inp, f"{prefix}.inputs[{i}]")
        
        # Validate outputs if present
        outputs = stage.get("outputs", [])
        if not isinstance(outputs, list):
            raise ManifestValidationError(f"{prefix}: outputs must be an array")
        for i, out in enumerate(outputs):
            self._validate_artifact_reference(out, f"{prefix}.outputs[{i}]")
        
        # Validate qualityGates if present
        quality_gates = stage.get("qualityGates", [])
        if not isinstance(quality_gates, list):
            raise ManifestValidationError(f"{prefix}: qualityGates must be an array")
        for i, gate in enumerate(quality_gates):
            self._validate_quality_gate(gate, f"{prefix}.qualityGates[{i}]")
        
        # Validate timeoutSeconds if present
        timeout = stage.get("timeoutSeconds")
        if timeout is not None:
            if not isinstance(timeout, int) or timeout < 1:
                raise ManifestValidationError(f"{prefix}: timeoutSeconds must be a positive integer")
        
        # Validate retryPolicy if present
        retry_policy = stage.get("retryPolicy")
        if retry_policy is not None:
            if not isinstance(retry_policy, dict):
                raise ManifestValidationError(f"{prefix}: retryPolicy must be an object")
            max_attempts = retry_policy.get("maxAttempts", 0)
            if not isinstance(max_attempts, int) or max_attempts < 0:
                raise ManifestValidationError(f"{prefix}: retryPolicy.maxAttempts must be a non-negative integer")
            backoff = retry_policy.get("backoffSeconds", 0)
            if not isinstance(backoff, int) or backoff < 0:
                raise ManifestValidationError(f"{prefix}: retryPolicy.backoffSeconds must be a non-negative integer")

    def _validate_artifact_reference(self, artifact: Dict[str, Any], path: str) -> None:
        """
        Validate an artifact reference.
        
        Args:
            artifact: Artifact reference dictionary to validate
            path: JSON path for error reporting
            
        Raises:
            ManifestValidationError: If artifact reference validation fails
        """
        # Check required fields
        if "artifactType" not in artifact:
            raise ManifestValidationError(f"{path}: missing required field 'artifactType'")
        if "artifactId" not in artifact:
            raise ManifestValidationError(f"{path}: missing required field 'artifactId'")
        
        # Validate field types
        if not isinstance(artifact.get("artifactType"), str):
            raise ManifestValidationError(f"{path}: artifactType must be a string")
        if not isinstance(artifact.get("artifactId"), str):
            raise ManifestValidationError(f"{path}: artifactId must be a string")
        
        # Validate optional fields if present
        version = artifact.get("version")
        if version is not None and not isinstance(version, str):
            raise ManifestValidationError(f"{path}: version must be a string")
        
        location = artifact.get("location")
        if location is not None and not isinstance(location, str):
            raise ManifestValidationError(f"{path}: location must be a string")
        
        # Note: producerStage and validationStatus are typically filled in by the orchestrator
        # during execution, so we don't require them in the manifest

    def _validate_quality_gate(self, gate: Dict[str, Any], path: str) -> None:
        """
        Validate a quality gate definition.
        
        Args:
            gate: Quality gate dictionary to validate
            path: JSON path for error reporting
            
        Raises:
            ManifestValidationError: If quality gate validation fails
        """
        # Check required fields
        if "gateId" not in gate:
            raise ManifestValidationError(f"{path}: missing required field 'gateId'")
        if "type" not in gate:
            raise ManifestValidationError(f"{path}: missing required field 'type'")
        
        # Validate field types
        if not isinstance(gate.get("gateId"), str):
            raise ManifestValidationError(f"{path}: gateId must be a string")
        if not isinstance(gate.get("type"), str):
            raise ManifestValidationError(f"{path}: type must be a string")
        
        # Validate config if present
        config = gate.get("config", {})
        if not isinstance(config, dict):
            raise ManifestValidationError(f"{path}: config must be an object")

    def _validate_version(self, version: Optional[str]) -> None:
        """
        Validate manifest version.
        
        Args:
            version: Version string from manifest
            
        Raises:
            ManifestVersionError: If version is unsupported
        """
        if version is None:
            raise ManifestVersionError("manifestVersion is required")
        
        if version not in self.SUPPORTED_VERSIONS:
            raise ManifestVersionError(
                f"Unsupported manifest version: {version}. "
                f"Supported versions: {', '.join(self.SUPPORTED_VERSIONS)}"
            )

    def _substitute_parameters(self, obj: Any, parameters: Dict[str, Any]) -> Any:
        """
        Recursively substitute parameters in a manifest object.
        
        Args:
            obj: Object to process (can be dict, list, string, or other)
            parameters: Dictionary of parameter names to values
            
        Returns:
            Object with parameters substituted
        """
        if isinstance(obj, dict):
            return {key: self._substitute_parameters(value, parameters) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_parameters(item, parameters) for item in obj]
        elif isinstance(obj, str):
            # Replace {{parameter_name}} with parameter value
            def replace_param(match):
                param_name = match.group(1)
                if param_name in parameters:
                    return str(parameters[param_name])
                else:
                    raise ManifestError(f"Parameter not found: {param_name}")
            
            return re.sub(r'\{\{\s*(\w+)\s*\}\}', replace_param, obj)
        else:
            return obj

    def get_stages(self) -> List[Dict[str, Any]]:
        """
        Get the list of stages from the parsed manifest.
        
        Returns:
            List of stage dictionaries
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        return self._manifest.get("stages", [])

    def get_workflow_id(self) -> str:
        """
        Get the workflow ID from the parsed manifest.
        
        Returns:
            Workflow ID string
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        return self._manifest.get("workflowId", "")

    def get_name(self) -> str:
        """
        Get the workflow name from the parsed manifest.
        
        Returns:
            Workflow name string
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        return self._manifest.get("name", "")

    def get_description(self) -> Optional[str]:
        """
        Get the workflow description from the parsed manifest.
        
        Returns:
            Workflow description string or None
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        return self._manifest.get("description")

    def get_global_quality_gates(self) -> List[Dict[str, Any]]:
        """
        Get the global quality gates from the parsed manifest.
        
        Returns:
            List of global quality gate dictionaries
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        return self._manifest.get("globalQualityGates", [])

    def to_model(self) -> ParameterizedManifest:
        """
        Convert the parsed manifest to a ParameterizedManifest model.
        
        Returns:
            ParameterizedManifest instance
            
        Raises:
            ManifestError: If no manifest has been parsed
        """
        if self._manifest is None:
            raise ManifestError("No manifest has been parsed. Call load_from_file or parse first.")
        
        # Convert stages to StageDefinition models
        stages = []
        for stage_dict in self._manifest.get("stages", []):
            stage = StageDefinition(
                stage_id=stage_dict["stageId"],
                agent_role=stage_dict["agentRole"],
                depends_on=stage_dict.get("dependsOn", []),
                inputs=[
                    ArtifactReference(
                        artifact_type=inp["artifactType"],
                        artifact_id=inp.get("artifactId", f"{stage_dict['stageId']}_input_{len(stage_dict.get('inputs', []))}"),
                        version=inp.get("version", "1.0.0"),
                        location=inp.get("location", "file:///default/input"),
                        producer_stage="",  # Will be filled during execution
                        validation_status="pending"  # Initial status
                    )
                    for inp in stage_dict.get("inputs", [])
                ],
                outputs=[
                    ArtifactReference(
                        artifact_type=out["artifactType"],
                        artifact_id=out.get("artifactId", f"{stage_dict['stageId']}_output_{len(stage_dict.get('outputs', []))}"),
                        version=out.get("version", "1.0.0"),
                        location=out.get("location", "file:///default/output"),
                        producer_stage="",  # Will be filled during execution
                        validation_status="pending"  # Initial status
                    )
                    for out in stage_dict.get("outputs", [])
                ],
                quality_gates=stage_dict.get("qualityGates", []),
                timeout_seconds=stage_dict.get("timeoutSeconds"),
                retry_policy=stage_dict.get("retryPolicy")
            )
            stages.append(stage)
        
        return ParameterizedManifest(
            manifest_version=self._manifest.get("manifestVersion", ""),
            workflow_id=self._manifest.get("workflowId", ""),
            name=self._manifest.get("name", ""),
            description=self._manifest.get("description"),
            stages=stages,
            global_quality_gates=self._manifest.get("globalQualityGates", []),
            parameters=self._parameters.copy()
        )


# Convenience function for loading a manifest
def load_manifest(file_path: str, parameters: Optional[Dict[str, Any]] = None) -> ParameterizedManifest:
    """
    Load a manifest from a file and convert to ParameterizedManifest model.
    
    Args:
        file_path: Path to the manifest JSON file
        parameters: Optional dictionary of parameters for substitution
        
    Returns:
        ParameterizedManifest instance
        
    Raises:
        ManifestError: If manifest cannot be loaded or parsed
        ManifestValidationError: If manifest structure is invalid
        ManifestVersionError: If manifest version is unsupported
    """
    parser = ManifestParser()
    if parameters:
        parser.set_parameters(parameters)
    manifest_dict = parser.load_from_file(file_path)
    return parser.to_model()