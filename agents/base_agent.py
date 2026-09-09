#!/usr/bin/env python3
"""
Base agent class for Ellio pipeline agents.
Provides common functionality for reading environment variables and handling artifacts.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse


@dataclass
class ArtifactReference:
    """Artifact reference matching the orchestration model."""
    artifact_type: str
    artifact_id: str
    version: str
    location: str
    producer_stage: str
    validation_status: str = "pending"


class BaseAgent:
    """Base class for all pipeline agents."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.inputs: List[ArtifactReference] = []
        self.parameters: Dict[str, Any] = {}
        self.stage_id: str = ""
        self._parse_environment()
    
    def _parse_environment(self):
        """Parse environment variables set by StageRunner."""
        # Parse input artifacts
        i = 0
        while True:
            artifact_type = os.environ.get(f"INPUT_{i}_TYPE")
            if artifact_type is None:
                break
            artifact_id = os.environ.get(f"INPUT_{i}_ID")
            version = os.environ.get(f"INPUT_{i}_VERSION")
            location = os.environ.get(f"INPUT_{i}_LOCATION")
            
            if all([artifact_type, artifact_id, version, location]):
                self.inputs.append(ArtifactReference(
                    artifact_type=artifact_type,
                    artifact_id=artifact_id,
                    version=version,
                    location=location,
                    producer_stage="",  # Will be filled from environment if needed
                    validation_status="pending"
                ))
            i += 1
        
        # Parse parameters
        for key, value in os.environ.items():
            if key.startswith("PARAM_"):
                param_name = key[6:].lower()  # Remove PARAM_ prefix
                self.parameters[param_name] = value
        
        # Get stage ID
        self.stage_id = os.environ.get("STAGE_STAGEID", "")
    
    def get_input_location(self, index: int = 0) -> Optional[str]:
        """Get the location of an input artifact by index."""
        if 0 <= index < len(self.inputs):
            return self.inputs[index].location
        return None
    
    def get_input_artifact(self, index: int = 0) -> Optional[ArtifactReference]:
        """Get an input artifact by index."""
        if 0 <= index < len(self.inputs):
            return self.inputs[index]
        return None
    
    def resolve_file_path(self, uri: str) -> Optional[Path]:
        """Resolve a file:// URI to a local Path."""
        if uri.startswith("file://"):
            return Path(uri[7:])
        return None
    
    def read_json_file(self, uri: str) -> Optional[dict]:
        """Read a JSON file from a file:// URI."""
        path = self.resolve_file_path(uri)
        if path and path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def write_json_file(self, uri: str, data: dict) -> bool:
        """Write a JSON file to a file:// URI."""
        path = self.resolve_file_path(uri)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        return False
    
    def copy_file(self, src_uri: str, dst_uri: str) -> bool:
        """Copy a file from source URI to destination URI."""
        src_path = self.resolve_file_path(src_uri)
        dst_path = self.resolve_file_path(dst_uri)
        
        if src_path and dst_path and src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return True
        return False
    
    def run(self) -> int:
        """Main entry point for the agent. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement run()")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message to stderr."""
        print(f"[{self.agent_name}] [{level}] {message}", file=sys.stderr)


def main():
    """Main entry point for agent scripts."""
    agent = create_agent()
    if agent is None:
        print("Failed to create agent", file=sys.stderr)
        sys.exit(1)
    
    try:
        exit_code = agent.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Agent error: {e}", file=sys.stderr)
        sys.exit(1)


def create_agent() -> Optional[BaseAgent]:
    """Factory function to create the specific agent. Override in agent scripts."""
    return None


if __name__ == "__main__":
    main()