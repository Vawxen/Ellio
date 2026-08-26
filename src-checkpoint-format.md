# Checkpoint Format for MVP Orchestration Spine

## 1. JSON Structure for Checkpoint Data

```json
{
  "checkpointId": "string",
  "timestamp": "string (ISO 8601)",
  "workflowId": "string",
  "currentStep": "string",
  "state": {
    // Arbitrary JSON representing workflow state
  },
  "decisionLogReference": {
    "logId": "string",
    "entryCount": "number"
  },
  "version": "string"
}
```

## 2. Explanation of Each Field

- **checkpointId**: Unique identifier for this checkpoint (UUID recommended)
- **timestamp**: When the checkpoint was created (ISO 8601 format)
- **workflowId**: Identifier of the workflow this checkpoint belongs to
- **currentStep**: The step identifier where execution is paused/resumed
- **state**: Serialized workflow state at the point of checkpointing. Contains all variables, data, and context needed to resume execution
- **decisionLogReference**: 
  - *logId*: Identifier of the decision log associated with this checkpoint
  - *entryCount*: Number of decision log entries up to this checkpoint
- **version**: Format version of the checkpoint (for evolution compatibility)

## 3. Relation to Decision Log Contract

The checkpoint maintains a reference to the decision log rather than duplicating decision data:
- Each checkpoint points to a specific decision log via `logId`
- The `entryCount` indicates how many decisions were recorded when the checkpoint was taken
- This allows reconstruction of the decision history up to the checkpoint point
- The decision log contract remains unchanged; checkpoints are complementary snapshots
- On resume, the system can replay decisions from the log up to the entry count to rebuild state if needed

## 4. Storage Considerations

- **Immutability**: Checkpoints should be treated as immutable once created
- **Storage Backend**: Designed for any key-value store (Redis, DynamoDB, etc.) or file system
- **Size Optimization**: 
  - State should contain only essential data for resumption
  - Large binary data should be stored separately with references in state
  - Consider delta checkpoints for workflows with large state
- **Retention Policy**: 
  - Configure based on workflow completion SLAs
  - Delete checkpoints after successful workflow completion
  - Retain failed workflow checkpoints for debugging (configurable period)
- **Performance**: 
  - Checkpoint creation should be asynchronous to avoid blocking workflow execution
  - Use efficient serialization (e.g., MessagePack, Protocol Buffers) for state if needed
  - Index by workflowId and timestamp for querying
- **Security**: 
  - Encrypt checkpoints at rest if containing sensitive data
  - Control access via workflow-level permissions