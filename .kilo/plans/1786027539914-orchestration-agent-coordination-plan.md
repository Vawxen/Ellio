# Orca Orchestration Agent Coordination Plan for Video Pipeline MVP

## Current State
- Orca orchestration run `run_ded6ef07ca33` active with objective "Coordinate video pipeline agents: tech-lead, research, design, coding"
- Three tasks dispatched to agent terminals:
  1. Research task (video AI models) → PowerShell terminal (`term_937f3bc8-496f-457b-ab01-f90fb36bb629`)
  2. Design task (manifest format) → tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
  3. Coding task (FFmpeg ingestion) → kimi-code agent terminal (`term_525835c1-0c78-4e4d-b4bc-00669cd5b28f`)
- Available agent terminals include additional kimi-code agents, PowerShell sessions, and Kilo CLI terminals
- Existing orchestration spine implementation provides manifest-driven execution, checkpointing, handoffs, and quality gates

## Objective
Enhance the video pipeline MVP by delegating specialized tasks to available agent agents using Orca orchestration, incorporating middle manager agents for coordination where appropriate, while maintaining focus on MVP-appropriate enhancements.

## Agent Resources Available
- **Tech-Lead Agent**: `term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69` (currently assigned to design task)
- **Research Agent**: `term_937f3bc8-496f-457b-ab01-f90fb36bb629` (currently assigned to research task)
- **Coding Agents**: 
  - `term_525835c1-0c78-4e4d-b4bc-00669cd5b28f` (currently assigned to coding task)
  - `term_f5c8283e-cb3f-4b91-9186-d995ab1f4221` (available)
- **Additional Terminals**: Multiple PowerShell/pty sessions and Kilo CLI terminals available for specialized agent assignment

## Planned Tasks and Delegation

### Phase 1: Task Definition and Agent Assignment
1. **Create additional pipeline stage tasks** for video transcription and translation
2. **Create quality gate enhancement tasks** for video-specific validation
3. **Create UX/UI design tasks** for pipeline monitoring interface
4. **Create middle manager coordination tasks** for architectural oversight and integration
5. **Assign tasks to appropriate agent terminals** based on specialization

### Phase 2: Dependency Management
- Establish logical dependencies between tasks (e.g., design depends on research)
- Use orchestration DAG capabilities to manage execution order
- Ensure middle manager agents review work before progression to dependent tasks

### Phase 3: Execution and Monitoring
- Monitor task progress using orchestration check/wait mechanisms
- Facilitate agent communication through orchestration messaging
- Manage escalations and blockers through coordinator intervention
- Validate completed work before acknowledging task completion

## Detailed Task Plan

### Research Enhancement Tasks
1. **Task**: Evaluate open-source video transcription models (Whisper.cpp, faster-whisper) for local deployment
   - **Agent**: Research PowerShell terminal (`term_937f3bc8-496f-457b-ab01-f90fb36bb629`)
   - **Output**: Model comparison report with accuracy, latency, and resource requirements
   - **Dependencies**: None

2. **Task**: Investigate video translation approaches (SeamlessM4T, MarianMT, cloud APIs)
   - **Agent**: Research PowerShell terminal (`term_937f3bc8-496f-457b-ab01-f90fb36bb629`)
   - **Output**: Translation strategy recommendation with implementation complexity assessment
   - **Dependencies**: None

### Design Enhancement Tasks
3. **Task**: Design standardized artifact contracts for video processing pipeline stages
   - **Agent**: Tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
   - **Output**: Artifact reference schema definitions for video frames, audio tracks, subtitles, metadata
   - **Dependencies**: Research tasks (1,2)

4. **Task**: Design UX/UI mockups for pipeline execution monitoring dashboard
   - **Agent**: Tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
   - **Output**: Wireframe designs for real-time stage progress, metrics visualization, and error tracking
   - **Dependencies**: Research tasks (1,2)

### Coding Implementation Tasks
5. **Task**: Implement video transcription stage using Whisper.cpp or faster-whisper
   - **Agent**: Available kimi-code agent terminal (`term_f5c8283e-cb3f-4b91-9186-d995ab1f4221`)
   - **Output**: FFmpeg-compatible stage implementation that produces transcription artifacts
   - **Dependencies**: Design task (3)

6. **Task**: Implement video translation stage using selected translation approach
   - **Agent**: Available kimi-code agent terminal (`term_f5c8283e-cb3f-4b91-9186-d995ab1f4221`)
   - **Output**: Stage implementation that produces translated subtitle/artifact outputs
   - **Dependencies**: Design task (3), Coding task (5)

7. **Task**: Enhance quality gate system with video-specific validation (duration, format, codec checks)
   - **Agent**: Available kimi-code agent terminal (`term_f5c8283e-cb3f-4b91-9186-d995ab1f4221`)
   - **Output**: Additional quality gate implementations for video artifact validation
   - **Dependencies**: Design task (3)

### Middle Manager Coordination Tasks
8. **Task**: Architectural review of pipeline stage implementations for contract compliance
   - **Agent**: Tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
   - **Output**: Review report ensuring all stages adhere to artifact reference and manifest contracts
   - **Dependencies**: Coding tasks (5,6,7)

9. **Task**: Integration testing coordination for end-to-end pipeline validation
   - **Agent**: Tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
   - **Output**: Test plan and execution script for validating research→design→coding workflow
   - **Dependencies**: Middle manager task (8)

10. **Task**: UX/UI design review and feedback consolidation
    - **Agent**: Tech-lead agent terminal (`term_9813ead4-b4dd-4cb0-b750-5d5bf6510b69`)
    - **Output**: Consolidated design feedback and implementation recommendations
    - **Dependencies**: Design task (4)

## Dependency Structure
```
Research Tasks (1,2) 
    � ↓
Design Tasks (3,4)
    � ↓
Coding Tasks (5,6,7) 
    � ↓
Middle Manager Review Tasks (8,9,10)
```

## Execution Instructions for Implementing Agent

1. **Verify Current State**:
   - Confirm orchestration run `run_ded6ef07ca33` is active: `orca orchestration run-show --id run_ded6ef07ca33 --json`
   - Check current task list: `orca orchestration task-list --json`

2. **Create New Tasks**:
   - Use `orca orchestration task-create --spec "<task_description>" --json` for each task above
   - Record returned task IDs for dependency creation

3. **Establish Dependencies**:
   - When creating dependent tasks, use `--deps '["<task_id_1>", "<task_id_2>"]'` JSON array format
   - Example: `orca orchestration task-create --spec "Design artifact contracts" --deps '["task_9e7db562d808","task_<translation_research_id>"]' --json`

4. **Dispatch Tasks to Agents**:
   - Use appropriate terminal handles from the Agent Resources section
   - Example: `orca orchestration dispatch --task <task_id> --to term_f5c8283e-cb3f-4b91-9186-d995ab1f4221 --json`

5. **Monitor Progress**:
   - Use `orca orchestration check --wait --types worker_done,escalation,question --timeout-ms 300000 --json` for 5-minute windows
   - Process messages, acknowledge completions, and handle escalations as needed
   - Use `orca orchestration task-list --json` to track status changes

6. **Leverage Middle Manager Agents**:
   - Before marking design tasks as complete, have tech-lead agent send review requests via orchestration ask
   - Use decision gates for approval workflows between phases
   - Have middle manager agents synthesize findings and provide consolidated feedback

## Validation Criteria
- All tasks completed with `worker_done` status and `--outcome succeeded`
- Middle manager review tasks confirm adherence to contracts and architectural integrity
- Dependencies properly enforced through orchestration DAG
- Agent communications tracked through orchestration messaging system
- Final deliverables compatible with existing orchestration spine implementation

## Open Questions for Clarification
1. Should we focus on implementing actual stage executions (5,6) or primarily on design/research for this phase?
2. Are there specific video processing use cases the user wants to prioritize (transcription, translation, summarization, etc.)?
3. What level of UX/UI fidelity is desired for the MVP (wireframes, mockups, or functional prototype)?
4. Should we create additional specialized agent terminals for QA, DevOps, or documentation roles?

## Next Steps for Implementing Agent
Begin with Phase 1 by creating the research enhancement tasks (1,2) and assigning them to the appropriate agent terminals, then proceed through the dependency chain as outlined.