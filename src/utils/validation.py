# src/utils/validation.py
"""
Validation utilities for the orchestration spine.
"""

import re
from typing import Union, List


def is_valid_semver(version: str) -> bool:
    """
    Check if a string is a valid semantic version (simplified).
    
    Args:
        version: Version string to check
        
    Returns:
        True if valid semver, False otherwise
    """
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def is_valid_uri(uri: str) -> bool:
    """
    Check if a string is a valid URI (basic validation).
    
    Args:
        uri: URI string to check
        
    Returns:
        True if valid URI format, False otherwise
    """
    # Basic URI validation - checks for scheme://
    pattern = r'^[a-zA-Z][a-zA-Z0-9+.-]*://.+'
    return bool(re.match(pattern, uri))


def is_not_empty_string(value: str) -> bool:
    """
    Check if a string is not empty or just whitespace.
    
    Args:
        value: String to check
        
    Returns:
        True if string contains non-whitespace characters, False otherwise
    """
    return isinstance(value, str) and bool(value.strip())


def validate_artifact_reference_fields(artifact: dict) -> List[str]:
    """
    Validate the fields of an artifact reference dictionary.
    
    Args:
        artifact: Dictionary representing an artifact reference
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    required_fields = ["artifactType", "artifactId", "version", "location", "producerStage", "validationStatus"]
    for field in required_fields:
        if field not in artifact:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(artifact[field], str):
            errors.append(f"Field '{field}' must be a string")
        elif not is_not_empty_string(artifact[field]):
            errors.append(f"Field '{field}' cannot be empty or whitespace-only")
    
    # If we have the basic fields, do more specific validation
    if "version" in artifact and isinstance(artifact["version"], str):
        if not is_valid_semver(artifact["version"]):
            errors.append("Field 'version' must be in semantic version format (major.minor.patch)")
    
    if "location" in artifact and isinstance(artifact["location"], str):
        if not is_valid_uri(artifact["location"]):
            errors.append("Field 'location' must be a valid URI")
    
    if "validationStatus" in artifact and isinstance(artifact["validationStatus"], str):
        if artifact["validationStatus"] not in ["pending", "passed", "failed", "skipped"]:
            errors.append("Field 'validationStatus' must be one of: pending, passed, failed, skipped")
    
    return errors