# Validation Approach for One Basic Quality Gate in MVP Orchestration Spine

## 1. Overview

For the MVP, we implement a single reusable quality gate: **Schema Validation**. This gate validates that artifact references and stage outputs conform to expected JSON schemas before allowing progression to the next stage.

## 2. Generic vs. Artifact-Specific Checks

### Generic Checks (Applied to All Artifacts)
These checks are performed on every artifact reference regardless of type:
- **Required Fields Presence**: All fields in the Artifact Reference Contract are present
  - `artifactType`, `artifactId`, `version`, `location`, `producerStage`, `validationStatus`
- **Field Types**: Each field is of the correct JSON type (string for all in MVP)
- **Non-Empty Strings**: String fields are not empty or whitespace-only
- **Version Format**: Version follows semantic versioning pattern (simplified: major.minor.patch)
- **URI Format**: Location field is a valid URI format (basic validation)

### Artifact-Specific Checks
These checks vary by artifact type and would be implemented as pluggable validators:
- For now, in MVP we define extension points but implement only one example:
  - **Transcript Artifact**: Validates that transcript JSON has required structure (segments array, text fields)
  - *Note: Full artifact-specific validation is deferred to future work; MVP focuses on generic schema validation*

## 3. Validation Results Representation

Validation results are represented as a structured object that feeds into the decision log:

```json
{
  "isValid": boolean,
  "validatedAt": "string (ISO 8601)",
  "artifactReference": {
    // The artifact reference that was validated
  },
  "genericCheckResults": {
    "requiredFieldsPresent": boolean,
    "fieldTypesCorrect": boolean,
    "nonEmptyStrings": boolean,
    "versionFormatValid": boolean,
    "uriFormatValid": boolean
  },
  "artifactSpecificCheckResults": {
    // Key-value pairs where key is check name, value is {passed: boolean, message?: string}
    // Empty if no artifact-specific checks configured for this type
  },
  "errors": [
    {
      "code": "string",
      "message": "string",
      "field": "string (optional)",
      "artifactReference": {
        // Reference to the artifact that caused this error
      }
    }
  ],
  "warnings": [
    {
      "code": "string",
      "message": "string",
      "field": "string (optional)"
    }
  ]
}
```

## 4. Quality Gate Decision Logic

The quality gate uses validation results to make a proceed/block decision:

```javascript
function makeQualityGateDecision(validationResults) {
  // Block if any generic check fails
  const genericChecksPassed = Object.values(validationResults.genericCheckResults).every(
    result => result === true
  );
  
  // Block if any validation errors exist
  const noErrors = validationResults.errors.length === 0;
  
  // For MVP, we consider artifact-specific warnings as non-blocking
  // In future, this could be configurable per artifact type
  
  return {
    decision: genericChecksPassed && noErrors ? "approved" : "rejected",
    rationale: genericChecksPassed && noErrors 
      ? "All generic validation checks passed and no errors found"
      : `Generic checks passed: ${genericChecksPassed}, Errors found: ${validationErrors.length > 0}`,
    relatedArtifacts: [validationResults.artifactReference]
  };
}
```

## 5. Integration with Orchestration Flow

1. **Before Stage Execution**: 
   - Optional: Validate input artifacts to ensure stage can proceed
   - If validation fails, stage is not executed and workflow halts

2. **After Stage Execution**:
   - Stage produces output artifacts and updates their validationStatus to "pending"
   - Orchestrator runs Schema Validation quality gate on all output artifacts
   - If gate passes, artifacts' validationStatus updated to "passed" and handoff proceeds
   - If gate fails, artifacts' validationStatus updated to "failed" and workflow halts

3. **Decision Log Entry**:
   - Each validation run creates a decision log entry with:
     - decision: "approved" or "rejected" from quality gate
     - rationale: Summary of validation results
     - relatedArtifacts: List of artifacts that were validated

## 6. Schema Definitions

### Artifact Reference Schema (JSON Schema Draft-07)
```json
{
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
  "additionalProperties": false
}
```

## 7. Extensibility Considerations

- **Pluggable Validators**: Artifact-specific validation logic can be added without changing core orchestration
- **Configurable Gates**: Different workflows could enable different quality gates (though MVP has one)
- **Validation Levels**: Strict vs. lenient modes could be introduced
- **Asynchronous Validation**: For large artifacts, validation could happen asynchronously with provisional handoffs

## 8. Example Validation Flow

1. Transcription stage completes, produces transcript artifact with validationStatus: "pending"
2. Orchestrator invokes Schema Validation quality gate on the transcript artifact
3. Generic checks pass (all required fields present, correct types, etc.)
4. Artifact-specific checks for transcript run (e.g., validates JSON structure)
5. All checks pass, no errors
6. Quality gate returns decision: "approved"
7. Orchestrator updates artifact validationStatus to "passed"
8. Handoff record created with the approved decision
9. Translation stage can now consume the transcript artifact
