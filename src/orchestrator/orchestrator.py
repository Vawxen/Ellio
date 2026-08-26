# src/orchestrator/orchestrator.py
"""
Main entry point for the orchestration spine.
"""

import argparse
import sys
import json
from typing import Dict, Any, Optional
from .manifest import load_manifest, ManifestParser
from .workflow_executor import WorkflowExecutor
from .state_persistence_manager_impl import StatePersistenceManagerImpl
from .execution_validation_manager_impl import ExecutionValidationManagerImpl
from .audit_manager_impl import AuditManagerImpl
from ..models.parameterized_manifest import ParameterizedManifest
from ..utils.config import config


def main():
    """Main entry point for the orchestration spine."""
    parser = argparse.ArgumentParser(
        description="Manifest-driven multi-agent video pipeline orchestrator"
    )
    parser.add_argument(
        "manifest",
        help="Path to the manifest JSON file"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Attempt to resume from checkpoint if available"
    )
    parser.add_argument(
        "--params",
        help="JSON string or path to JSON file containing parameters for manifest substitution"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (not implemented in MVP)"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration if provided
        if args.config:
            with open(args.config, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                # In a full implementation, we would update the global config
                # For MVP, we'll just note that config loading is supported
        
        # Load parameters if provided
        parameters: Optional[Dict[str, Any]] = None
        if args.params:
            try:
                # Try to parse as JSON string first
                parameters = json.loads(args.params)
            except json.JSONDecodeError:
                # If that fails, try to load as a file
                try:
                    with open(args.params, 'r', encoding='utf-8') as f:
                        parameters = json.load(f)
                except FileNotFoundError:
                    print(f"Error: Parameter file not found: {args.params}", file=sys.stderr)
                    sys.exit(1)
                except json.JSONDecodeError as e:
                    print(f"Error: Invalid JSON in parameter file: {e}", file=sys.stderr)
                    sys.exit(1)
        
        # Load and parse manifest
        print(f"Loading manifest from: {args.manifest}")
        manifest = load_manifest(args.manifest, parameters)
        print(f"Loaded manifest for workflow: {manifest.workflow_id}")
        
        # Create strategy instances
        state_persistence_manager = StatePersistenceManagerImpl()
        execution_validation_manager = ExecutionValidationManagerImpl()
        audit_manager = AuditManagerImpl()
        
        # Create and run workflow executor with strategies
        executor = WorkflowExecutor(
            state_persistence_manager=state_persistence_manager,
            execution_validation_manager=execution_validation_manager,
            audit_manager=audit_manager
        )
        print("Starting workflow execution...")
        
        final_state = executor.execute_workflow(
            manifest=manifest,
            resume_from_checkpoint=args.resume
        )
        
        # Output final result
        print(f"Workflow completed with status: {final_state.status}")
        print(f"Completed stages: {final_state.completed_stages}")
        
        if final_state.failed_stage:
            print(f"Failed stage: {final_state.failed_stage}")
        
        # Return appropriate exit code
        if final_state.status == "completed":
            sys.exit(0)
        elif final_state.status == "failed":
            sys.exit(1)
        elif final_state.status == "cancelled":
            sys.exit(2)
        else:
            sys.exit(3)
            
    except KeyboardInterrupt:
        print("\nWorkflow execution interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()