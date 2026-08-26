# Handoff Format for MVP Orchestration Spine

## 1. JSON Structure for Handoff Records

```json
{
  "handoffId": "string",
  "timestamp": "string (ISO 8601)",
  "fromStage": "string",
  "toStage": "string",
  "workflowId": "string",
  "artifacts": [
    {
      "artifactType": "string",
      "artifactId": "string",
      "version": "string",
      "location": "string",
      "producerStage": "string",
      "validationStatus": "string"
    }
  ],
  "decision": {
    "decision": "string",
    "rationale": "string",
    "relatedArtifacts": [
      {
        "artifactType": "string",
        "artifactId": "string"
      }
    ]
  },
  "version": "string"
}
```

## 2. Explanation of Each Field

- **handoffId**: Unique identifier for this handoff record (UUID recommended)
- **timestamp**: When the handoff occurred (ISO 8601 format)
- **fromStage**: The stage identifier that produced the output
- **toStage**: The stage identifier that will consume the output
- **workflowId**: Identifier of the workflow this handoff belongs to
- **artifacts**: Array of artifact references being passed from `fromStage` to `toStage`
  - Each artifact follows the **Artifact Reference Contract**:
    - *artifactType*: Type/category of the artifact (e.g., "video", "audio", "transcript")
    - *artifactId*: Unique identifier for the artifact
    - *version*: Version of the artifact
    - *location*: Where the artifact is stored (URI, path, etc.)
    - *producerStage*: Stage that created/produced this artifact
    - *validationStatus*: Status from quality gates (e.g., "passed", "failed", "pending")
- **decision**: The quality gate decision that authorized this handoff
  - *decision*: The decision outcome (e.g., "approved", "rejected", "needs_revision")
  - *rationale*: Explanation for the decision
  - *relatedArtifacts*: Artifacts that influenced this decision (references to artifact IDs and types)
- **version**: Format version of the handoff record (for evolution compatibility)

## 3. Relation to Decision Log Contract

Handoff records are complementary to the decision log:
- Each handoff is associated with a specific quality gate decision
- The `decision` field in the handoff mirrors an entry in the decision log
- Decision log entries contain more detailed context about the decision-making process
- Handoff records focus on the practical transfer of artifacts between stages
- Together, they provide a complete audit trail: decision → handoff → execution

## 4. Storage Considerations

- **Immutability**: Handoff records should be treated as immutable once created
- **Storage Backend**: Designed for any key-value store, document database, or file system
- **Relationship to Checkpoints**: 
  - Handoffs occur between stages; checkpoints capture workflow state at specific points
  - A checkpoint may include references to recent handoffs
  - On resume, the system can reconstruct the artifact flow from handoff records
- **Size Optimization**: 
  - Artifact references should be lightweight (avoid embedding large binary data)
  - The `location` field points to where the actual artifact is stored
- **Querying**: 
  - Index by workflowId to trace artifact lineage
  - Index by fromStage/toStage to understand stage dependencies
  - Index by timestamp for temporal analysis

## 5. Example Handoff Record

```json
{
  "handoffId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-08-06T17:30:00+01:00",
  "fromStage": "transcription",
  "toStage": "translation",
  "workflowId": "workflow_123",
  "artifacts": [
    {
      "artifactType": "transcript",
      "artifactId": "transcript_abc",
      "version": "1.0",
      "location": "s3://bucket/transcripts/video123_v1.json",
      "producerStage": "transcription",
      "validationStatus": "passed"
    }
  ],
  "decision": {
    "decision": "approved",
    "rationale": "Transcript meets accuracy threshold of 95%",
    "relatedArtifacts": [
      {
        "artifactType": "video",
        "artifactId": "video123"
      }
    ]
  },
  "version": "1.0"
}
```