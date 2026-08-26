# Codebase Design Improvement Plan

## Overview
This plan outlines improvements to make the manifest-driven video pipeline orchestration spine follow deep module principles: small interfaces with lots of implementation hidden behind them, clear seams for adaptability, and improved testability.

## Current State Analysis
The WorkflowExecutor class is a God object that:
- Has a large interface with multiple responsibilities
- Directly instantiates all dependencies (tight coupling)
- Handles orchestration, state management, checkpointing, logging, quality gates, and handoffs
- Is difficult to test due to tight coupling

## Improvement Goals
1. **Reduce WorkflowExecutor interface size** - Focus on core orchestration logic only
2. **Introduce clear seams** - Create abstractions for swappable components
3. **Improve locality** - Concentrate related functionality in focused modules
4. **Increase leverage** - Enable reuse across different contexts
5. **Enhance testability** - Make dependencies injectable and mockable

## Specific Refactorings

### 1. WorkflowExecutor Refactoring
**Current Issues:**
- Too many responsibilities (violates Single Responsibility Principle)
- Large interface with many public methods
- Direct instantiation of dependencies (hard to test/swap)

**Proposed Changes:**
- Extract orchestration logic into a separate `OrchestrationStrategy` interface
- Move state management to a dedicated `StateManager` 
- Introduce dependency injection for all manager components
- Reduce public interface to essential orchestration methods only

### 2. Introduce Abstraction Boundaries
Create clear seams for:
- **Persistence Strategy** - Abstract checkpointing and storage
- **Execution Strategy** - Abstract stage execution mechanisms  
- **Validation Strategy** - Abstract quality gate implementations
- **Logging Strategy** - Abstract decision logging/audit trails

### 3. Improve Manager Interfaces
Review and refine manager classes to have:
- Smaller, more focused interfaces
- Clear single responsibilities
- Better encapsulation of implementation details

## Implementation Approach

### Phase 1: Define Core Abstractions
Create interface definitions for:
- `IStateManager` - Handles workflow state operations
- `IPersistenceStrategy` - Handles checkpointing and state persistence
- `IExecutionStrategy` - Handles stage execution mechanisms
- `IValidationStrategy` - Handles quality gate validations
- `IAuditStrategy` - Handles decision logging and audit trails

### Phase 2: Refactor WorkflowExecutor
- Reduce to orchestration coordinator role only
- Accept dependencies via constructor injection
- Delegate specific concerns to appropriate strategy objects
- Maintain minimal public interface focused on workflow lifecycle

### Phase 3: Update Dependencies
Update all calling code to work with the new abstractions
Ensure backward compatibility where possible
Update configuration and instantiation logic

## Expected Benefits
1. **Smaller Interface** - WorkflowExecutor public methods reduced by ~60%
2. **Better Testability** - All dependencies injectable and mockable
3. **Improved Locality** - Related functionality concentrated in focused modules
4. **Enhanced Flexibility** - Easy to swap implementations (e.g., different storage backends)
5. **Clearer Responsibilities** - Each module has a single, well-defined purpose
6. **Easier Maintenance** - Changes isolated to specific modules

## Risk Mitigation
- Maintain backward compatibility during transition
- Phase refactorings to ensure working system at each step
- Comprehensive test coverage before and after changes
- Clear documentation of new interfaces and contracts

## Success Metrics
- Reduction in WorkflowExecutor public method count
- Increased testability (measured by ease of mocking dependencies)
- Clear separation of concerns (each module has single responsibility)
- Ability to swap implementations without changing core logic