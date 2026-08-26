# src/orchestrator/quality_gate.py
"""
Quality gate engine for validating artifact references.
"""

import jsonschema
from typing import List, Dict, Any, Optional
from ..models.artifact_reference import ArtifactReference
from ..models.validation_result import ValidationResult
from ..utils.validation import validate_artifact_reference_fields
from ..utils.config import config
import datetime


class QualityGateError(Exception):
    """Base exception for quality gate errors."""
    pass


class QualityGateEngine:
    """
    Executes quality gate validations on artifact references.
    """
    
    def __init__(self):
        """Initialize quality gate engine."""
        self.config = config
        # Cache for loaded schemas to avoid repeated file I/O
        self._schema_cache: Dict[str, dict] = {}
    
    def validate_artifact(self, artifact: ArtifactReference,
                         gate_config: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate an artifact reference using the specified quality gate.
        
        Args:
            artifact: Artifact reference to validate
            gate_config: Quality gate configuration (for MVP, this specifies schema validation)
            
        Returns:
            ValidationResult with validation outcome
            
        Raises:
            QualityGateError: If validation cannot be performed
        """
        try:
            # For MVP, we implement schema validation as the basic quality gate
            # In the future, this could support multiple gate types
            
            validation_result = ValidationResult(
                is_valid=True,  # Assume valid until proven otherwise
                validated_at=datetime.datetime.utcnow(),
                artifact_reference=artifact
            )
            
            # Perform generic checks (apply to all artifacts)
            self._perform_generic_checks(artifact, validation_result)
            
            # Perform schema validation if configured
            if gate_config and gate_config.get("type") == "schemaValidation":
                self._perform_schema_validation(artifact, gate_config, validation_result)
            
            # For MVP, we don't implement artifact-specific checks yet
            # They would be added here in future extensions
            
            # Determine overall validity
            validation_result.is_valid = (
                all(validation_result.generic_check_results.values()) and
                len(validation_result.errors) == 0
            )
            
            return validation_result
        except Exception as e:
            raise QualityGateError(f"Failed to validate artifact: {e}")
    
    def _perform_generic_checks(self, artifact: ArtifactReference,
                              validation_result: ValidationResult) -> None:
        """
        Perform generic validation checks on an artifact reference.
        
        Args:
            artifact: Artifact reference to validate
            validation_result: ValidationResult to update
        """
        # Required fields presence
        required_fields = ["artifact_type", "artifact_id", "version", "location", 
                          "producer_stage", "validation_status"]
        missing_fields = []
        for field in required_fields:
            value = getattr(artifact, field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        
        validation_result.add_generic_check(
            "requiredFieldsPresent", 
            len(missing_fields) == 0
        )
        
        if missing_fields:
            validation_result.add_error(
                "MISSING_REQUIRED_FIELDS",
                f"Missing required fields: {', '.join(missing_fields)}",
                artifact_reference=artifact
            )
        
        # Field types (already validated by ArtifactReference constructor, but double-check)
        validation_result.add_generic_check("fieldTypesCorrect", True)
        
        # Non-empty strings
        string_fields = [
            ("artifact_type", artifact.artifact_type),
            ("artifact_id", artifact.artifact_id),
            ("version", artifact.version),
            ("location", artifact.location),
            ("producer_stage", artifact.producer_stage),
            ("validation_status", artifact.validation_status)
        ]
        
        empty_fields = []
        for field_name, value in string_fields:
            if not isinstance(value, str) or not value.strip():
                empty_fields.append(field_name)
        
        validation_result.add_generic_check(
            "nonEmptyStrings", 
            len(empty_fields) == 0
        )
        
        if empty_fields:
            validation_result.add_error(
                "EMPTY_STRING_FIELD",
                f"Fields cannot be empty or whitespace-only: {', '.join(empty_fields)}",
                artifact_reference=artifact
            )
        
        # Version format
        version_valid = self._is_valid_semver(artifact.version)
        validation_result.add_generic_check("versionFormatValid", version_valid)
        
        if not version_valid:
            validation_result.add_error(
                "INVALID_VERSION_FORMAT",
                f"Version must be in semantic version format (major.minor.patch): {artifact.version}",
                artifact_reference=artifact
            )
        
        # URI format
        uri_valid = self._is_valid_uri(artifact.location)
        validation_result.add_generic_check("uriFormatValid", uri_valid)
        
        if not uri_valid:
            validation_result.add_error(
                "INVALID_URI_FORMAT",
                f"Location must be a valid URI: {artifact.location}",
                artifact_reference=artifact
            )
        
        # Validation status enum
        validation_status_valid = artifact.validation_status in ["pending", "passed", "failed", "skipped"]
        validation_result.add_generic_check("validationStatusEnumValid", validation_status_valid)
        
        if not validation_status_valid:
            validation_result.add_error(
                "INVALID_VALIDATION_STATUS",
                f"Validation status must be one of: pending, passed, failed, skipped: {artifact.validation_status}",
                artifact_reference=artifact
            )
    
    def _perform_schema_validation(self, artifact: ArtifactReference,
                                 gate_config: Dict[str, Any],
                                 validation_result: ValidationResult) -> None:
        """
        Perform JSON schema validation on an artifact reference.
        
        Args:
            artifact: Artifact reference to validate
            gate_config: Quality gate configuration with schema details
            validation_result: ValidationResult to update
        """
        try:
            # Get schema URI from config
            schema_uri = gate_config.get("config", {}).get("schemaUri")
            if not schema_uri:
                # For MVP, we'll use a default schema if none specified
                # In reality, this should be an error or use built-in schema
                schema_uri = "schemas/artifact-reference-v1.json"
            
            # Load schema (with caching)
            schema = self._load_schema(schema_uri)
            
            # Convert artifact to dictionary for validation
            artifact_dict = artifact.to_dict()
            
            # Perform validation
            jsonschema.validate(instance=artifact_dict, schema=schema)
            
            # If we reach here, validation passed
            validation_result.add_generic_check("schemaValidationPassed", True)
            
        except jsonschema.exceptions.ValidationError as e:
            validation_result.add_generic_check("schemaValidationPassed", False)
            validation_result.add_error(
                "SCHEMA_VALIDATION_FAILED",
                f"Schema validation failed: {e.message}",
                field=e.path[-1] if e.path else None,
                artifact_reference=artifact
            )
        except Exception as e:
            validation_result.add_generic_check("schemaValidationPassed", False)
            validation_result.add_error(
                "SCHEMA_LOAD_ERROR",
                f"Failed to load or apply schema: {e}",
                artifact_reference=artifact
            )
    
    def _load_schema(self, schema_uri: str) -> dict:
        """
        Load a JSON schema from URI (with caching).
        
        Args:
            schema_uri: URI of the schema to load
            
        Returns:
            Schema dictionary
        """
        # Return cached schema if available
        if schema_uri in self._schema_cache:
            return self._schema_cache[schema_uri]
        
        try:
            # For MVP, we'll handle file:// URIs and provide a default schema
            if schema_uri.startswith("file://"):
                file_path = schema_uri[7:]  # Remove file:// prefix
                with open(file_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
            else:
                # For other URIs, we would use HTTP requests in a full implementation
                # For MVP, we'll fall back to a built-in schema
                schema = self._get_default_artifact_schema()
            
            # Cache the schema
            self._schema_cache[schema_uri] = schema
            return schema
        except Exception:
            # If we can't load the specified schema, fall back to default
            return self._get_default_artifact_schema()
    
    def _get_default_artifact_schema(self) -> dict:
        """
        Get the default JSON schema for artifact references.
        
        Returns:
            Default schema dictionary
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "ArtifactReference",
            "type": "object",
            "required": ["artifactType", "artifactId", "version", "location", "producerStage", "validationStatus"],
            "properties": {
                "artifactType": {
                    "type": "string",
                    "minLength": 1
                },
                "artifactId": {
                    "type": "string",
                    "minLength": 1
                },
                "version": {
                    "type": "string",
                    "pattern": "^\\d+\\.\\d+\\.\\d+$"
                },
                "location": {
                    "type": "string",
                    "format": "uri"
                },
                "producerStage": {
                    "type": "string",
                    "minLength": 1
                },
                "validationStatus": {
                    "type": "string",
                    "enum": ["pending", "passed", "failed", "skipped"]
                }
            },
            "additionalProperties": False
        }
    
    def _is_valid_semver(self, version: str) -> bool:
        """
        Check if a string is a valid semantic version (simplified).
        
        Args:
            version: Version string to check
            
        Returns:
            True if valid semver, False otherwise
        """
        import re
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
    
    def _is_valid_uri(self, uri: str) -> bool:
        """
        Check if a string is a valid URI (basic validation).
        
        Args:
            uri: URI string to check
            
        Returns:
            True if valid URI format, False otherwise
        """
        import re
        # Basic URI validation - checks for scheme://
        pattern = r'^[a-zA-Z][a-zA-Z0-9+.-]*://.+'
        return bool(re.match(pattern, uri))
    
    def make_quality_gate_decision(self, validation_result: ValidationResult) -> Dict[str, Any]:
        """
        Make a quality gate decision based on validation results.
        
        Args:
            validation_result: Results from artifact validation
            
        Returns:
            Decision dictionary compatible with decision log contract
        """
        # Block if any generic check fails
        generic_checks_passed = all(validation_result.generic_check_results.values())
        
        # Block if any validation errors exist
        no_errors = len(validation_result.errors) == 0
        
        # For MVP, we consider artifact-specific warnings as non-blocking
        # In future, this could be configurable per artifact type
        
        decision = "approved" if (generic_checks_passed and no_errors) else "rejected"
        
        if decision == "approved":
            rationale = "All generic validation checks passed and no errors found"
        else:
            failed_checks = [name for name, passed in validation_result.generic_check_results.items() if not passed]
            rationale_parts = []
            if failed_checks:
                rationale_parts.append(f"Failed generic checks: {', '.join(failed_checks)}")
            if validation_result.errors:
                rationale_parts.append(f"Validation errors: {len(validation_result.errors)} error(s)")
            rationale = "; ".join(rationale_parts) if rationale_parts else "Validation failed"
        
        return {
            "decision": decision,
            "rationale": rationale,
            "relatedArtifacts": [validation_result.artifact_reference]
        }