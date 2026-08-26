# src/models/validation_result.py
"""
Validation result model for quality gate outcomes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .artifact_reference import ArtifactReference


@dataclass
class ValidationResult:
    """
    Results of running a quality gate validation on an artifact reference.
    """
    is_valid: bool
    validated_at: datetime
    artifact_reference: ArtifactReference
    generic_check_results: Dict[str, bool] = field(default_factory=dict)
    artifact_specific_check_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not isinstance(self.is_valid, bool):
            raise ValueError("is_valid must be a boolean")
        if not isinstance(self.validated_at, datetime):
            raise ValueError("validated_at must be a datetime instance")
        if not isinstance(self.artifact_reference, ArtifactReference):
            raise ValueError("artifact_reference must be an ArtifactReference instance")
        if not isinstance(self.generic_check_results, dict):
            raise ValueError("generic_check_results must be a dictionary")
        for check_name, result in self.generic_check_results.items():
            if not isinstance(check_name, str):
                raise ValueError("generic_check_results keys must be strings")
            if not isinstance(result, bool):
                raise ValueError("generic_check_results values must be booleans")
        if not isinstance(self.artifact_specific_check_results, dict):
            raise ValueError("artifact_specific_check_results must be a dictionary")
        for check_name, result_dict in self.artifact_specific_check_results.items():
            if not isinstance(check_name, str):
                raise ValueError("artifact_specific_check_results keys must be strings")
            if not isinstance(result_dict, dict):
                raise ValueError("artifact_specific_check_results values must be dictionaries")
            if "passed" not in result_dict:
                raise ValueError("artifact_specific_check_results items must have 'passed' field")
            if not isinstance(result_dict["passed"], bool):
                raise ValueError("artifact_specific_check_results['passed'] must be a boolean")
            if "message" in result_dict and not isinstance(result_dict["message"], str):
                raise ValueError("artifact_specific_check_results['message'] must be a string if present")
        if not isinstance(self.errors, list):
            raise ValueError("errors must be a list")
        for error in self.errors:
            if not isinstance(error, dict):
                raise ValueError("errors items must be dictionaries")
            if "code" not in error or "message" not in error:
                raise ValueError("errors items must have 'code' and 'message' fields")
            if not isinstance(error["code"], str) or not isinstance(error["message"], str):
                raise ValueError("errors['code'] and errors['message'] must be strings")
            if "field" in error and not isinstance(error["field"], str):
                raise ValueError("errors['field'] must be a string if present")
            if "artifactReference" in error:
                if not isinstance(error["artifactReference"], dict):
                    raise ValueError("errors['artifactReference'] must be a dictionary if present")
                # Validate it's a valid artifact reference dict
                ArtifactReference.from_dict(error["artifactReference"])  # Will raise if invalid
        if not isinstance(self.warnings, list):
            raise ValueError("warnings must be a list")
        for warning in self.warnings:
            if not isinstance(warning, dict):
                raise ValueError("warnings items must be dictionaries")
            if "code" not in warning or "message" not in warning:
                raise ValueError("warnings items must have 'code' and 'message' fields")
            if not isinstance(warning["code"], str) or not isinstance(warning["message"], str):
                raise ValueError("warnings['code'] and warnings['message'] must be strings")
            if "field" in warning and not isinstance(warning["field"], str):
                raise ValueError("warnings['field'] must be a string if present")

    def to_dict(self) -> dict:
        """
        Convert to dictionary representation for serialization.
        
        Returns:
            Dictionary representation of the validation result
        """
        return {
            "isValid": self.is_valid,
            "validatedAt": self.validated_at.isoformat(),
            "artifactReference": self.artifact_reference.to_dict(),
            "genericCheckResults": self.generic_check_results,
            "artifactSpecificCheckResults": self.artifact_specific_check_results,
            "errors": self.errors,
            "warnings": self.warnings
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationResult':
        """
        Create ValidationResult from dictionary.
        
        Args:
            data: Dictionary with validation result data
            
        Returns:
            ValidationResult instance
        """
        return cls(
            is_valid=data["isValid"],
            validated_at=datetime.fromisoformat(data["validatedAt"]),
            artifact_reference=ArtifactReference.from_dict(data["artifactReference"]),
            generic_check_results=data.get("genericCheckResults", {}),
            artifact_specific_check_results=data.get("artifactSpecificCheckResults", {}),
            errors=data.get("errors", []),
            warnings=data.get("warnings", [])
        )

    def add_generic_check(self, check_name: str, passed: bool) -> None:
        """
        Add a generic check result.
        
        Args:
            check_name: Name of the check
            passed: Whether the check passed
        """
        self.generic_check_results[check_name] = passed

    def add_artifact_specific_check(self, check_name: str, passed: bool, message: Optional[str] = None) -> None:
        """
        Add an artifact-specific check result.
        
        Args:
            check_name: Name of the check
            passed: Whether the check passed
            message: Optional message with details
        """
        result_dict = {"passed": passed}
        if message is not None:
            result_dict["message"] = message
        self.artifact_specific_check_results[check_name] = result_dict

    def add_error(self, code: str, message: str, field: Optional[str] = None, 
                  artifact_reference: Optional[ArtifactReference] = None) -> None:
        """
        Add a validation error.
        
        Args:
            code: Error code
            message: Error message
            field: Optional field that caused the error
            artifact_reference: Optional artifact reference related to the error
        """
        error_dict = {"code": code, "message": message}
        if field is not None:
            error_dict["field"] = field
        if artifact_reference is not None:
            error_dict["artifactReference"] = artifact_reference.to_dict()
        self.errors.append(error_dict)

    def add_warning(self, code: str, message: str, field: Optional[str] = None) -> None:
        """
        Add a validation warning.
        
        Args:
            code: Warning code
            message: Warning message
            field: Optional field related to the warning
        """
        warning_dict = {"code": code, "message": message}
        if field is not None:
            warning_dict["field"] = field
        self.warnings.append(warning_dict)