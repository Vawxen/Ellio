#!/usr/bin/env python3
"""
Video Effects Agent for Ellio pipeline.
Applies video filters, transitions, and basic color correction.
"""

import os
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent, ArtifactReference


class VideoEffectsAgent(BaseAgent):
    """Video effects processing agent."""
    
    def __init__(self):
        super().__init__("video-effects-agent")
    
    def process(self, inputs, outputs, parameters):
        """
        Apply video effects to input video.
        
        Expected inputs:
        - video: Input video file
        
        Expected outputs:
        - video: Processed video file
        """
        # Get input video path
        video_input = self.get_input_path(inputs, 'video')
        if not video_input:
            raise ValueError("Missing required input: video")
        
        # Get output video path
        video_output = self.get_output_path(outputs, 'video')
        if not video_output:
            raise ValueError("Missing required output: video")
        
        # Get parameters for effects
        # Default parameters if none provided
        brightness = parameters.get('brightness', 0)  # -1.0 to 1.0
        contrast = parameters.get('contrast', 1.0)    # 0.0 to 2.0
        saturation = parameters.get('saturation', 1.0)  # 0.0 to 3.0
        
        # Build ffmpeg filter string
        filters = []
        if brightness != 0:
            filters.append(f"eq=brightness={brightness}")
        if contrast != 1.0:
            if filters:
                filters[-1] += f":contrast={contrast}"
            else:
                filters.append(f"eq=contrast={contrast}")
        if saturation != 1.0:
            if filters:
                filters[-1] += f":saturation={saturation}"
            else:
                filters.append(f"eq=saturation={saturation}")
        
        filter_string = ",".join(filters) if filters else None
        
        # Build ffmpeg command
        cmd = ['ffmpeg', '-i', video_input]
        
        if filter_string:
            cmd.extend(['-vf', filter_string])
        
        # Video codec settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            video_output,
            '-y'
        ])
        
        self.logger.info(f"Applying video effects: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Video effects failed: {result.stderr}")
            raise RuntimeError(f"Video effects failed: {result.stderr}")
        
        # Validate output file exists and has content
        if not os.path.exists(video_output) or os.path.getsize(video_output) == 0:
            raise RuntimeError("Video effects produced empty or missing file")
        
        self.logger.info(f"Video effects applied successfully: {video_output}")
        
        # Create output artifact reference
        output_artifact = ArtifactReference(
            artifact_type="video",
            artifact_id=os.path.basename(video_output),
            version="1.0",
            location=f"file://{os.path.abspath(video_output)}",
            producer_stage=self.stage_id,
            validation_status="passed"
        )
        
        return [output_artifact]


if __name__ == "__main__":
    agent = VideoEffectsAgent()
    agent.run()