#!/usr/bin/env python3
"""
Metadata Extraction Agent for Ellio pipeline.
Extracts technical metadata from video files using ffprobe.
"""

import os
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent, ArtifactReference


class MetadataAgent(BaseAgent):
    """Metadata extraction agent."""
    
    def __init__(self):
        super().__init__("metadata-agent")
    
    def process(self, inputs, outputs, parameters):
        """
        Extract metadata from video file.
        
        Expected inputs:
        - video: Input video file
        
        Expected outputs:
        - metadata: JSON file containing technical metadata
        """
        # Get input video path
        video_input = self.get_input_path(inputs, 'video')
        if not video_input:
            raise ValueError("Missing required input: video")
        
        # Get output metadata path
        metadata_output = self.get_output_path(outputs, 'metadata')
        if not metadata_output:
            raise ValueError("Missing required output: metadata")
        
        # Use ffprobe to extract metadata
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_input
        ]
        
        self.logger.info(f"Extracting metadata: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Metadata extraction failed: {result.stderr}")
            raise RuntimeError(f"Metadata extraction failed: {result.stderr}")
        
        # Parse the JSON output
        try:
            metadata = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse metadata JSON: {e}")
            raise RuntimeError(f"Failed to parse metadata JSON: {e}")
        
        # Write metadata to output file
        with open(metadata_output, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Validate output file exists and has content
        if not os.path.exists(metadata_output) or os.path.getsize(metadata_output) == 0:
            raise RuntimeError("Metadata extraction produced empty or missing file")
        
        self.logger.info(f"Metadata extracted successfully: {metadata_output}")
        
        # Create output artifact reference
        output_artifact = ArtifactReference(
            artifact_type="metadata",
            artifact_id=os.path.basename(metadata_output),
            version="1.0",
            location=f"file://{os.path.abspath(metadata_output)}",
            producer_stage=self.stage_id,
            validation_status="passed"
        )
        
        return [output_artifact]


if __name__ == "__main__":
    agent = MetadataAgent()
    agent.run()