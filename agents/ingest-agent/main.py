#!/usr/bin/env python3
"""
Ingest Agent for Ellio Pipeline.
Handles video file ingestion - copies and validates source video to output location.
"""

import sys
import os
from pathlib import Path

# Add the agents directory to path for base_agent import
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_agent import BaseAgent, ArtifactReference, main


class IngestAgent(BaseAgent):
    """Agent for ingesting video files."""
    
    def __init__(self):
        super().__init__("ingest-agent")
    
    def run(self) -> int:
        """Execute the ingestion stage."""
        self.log("Starting video ingestion")
        
        # Get input video location
        input_location = self.get_input_location(0)
        if not input_location:
            self.log("No input video provided", "ERROR")
            return 1
        
        self.log(f"Input video: {input_location}")
        
        # Get output location from environment or parameters
        output_location = os.environ.get("OUTPUT_0_LOCATION")
        if not output_location:
            # Try to get from stage outputs definition
            for key, value in os.environ.items():
                if key.startswith("STAGE_OUTPUTS"):
                    # This would be complex to parse, so we'll use a simpler approach
                    pass
        
        # For MVP, we'll check if there's an expected output in the stage definition
        # The StageRunner creates placeholder outputs, so we need to find our output
        output_location = self._get_output_location()
        
        if not output_location:
            self.log("No output location specified", "ERROR")
            return 1
        
        self.log(f"Output location: {output_location}")
        
        # Resolve file paths
        src_path = self.resolve_file_path(input_location)
        dst_path = self.resolve_file_path(output_location)
        
        if not src_path or not dst_path:
            self.log("Invalid file URIs", "ERROR")
            return 1
        
        if not src_path.exists():
            self.log(f"Source file does not exist: {src_path}", "ERROR")
            return 1
        
        # Copy the video file
        try:
            self.log(f"Copying {src_path} to {dst_path}")
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(src_path, dst_path)
            self.log("Video ingestion completed successfully")
            return 0
        except Exception as e:
            self.log(f"Failed to copy video: {e}", "ERROR")
            return 1
    
    def _get_output_location(self) -> Optional[str]:
        """Get the output location from stage definition or environment."""
        # Check if there's an OUTPUT_0_LOCATION or similar
        for key, value in os.environ.items():
            if key.startswith("OUTPUT_") and key.endswith("_LOCATION"):
                return value
        
        # Fallback: use parameter
        return self.parameters.get("output_location")


def create_agent() -> BaseAgent:
    return IngestAgent()


if __name__ == "__main__":
    main()