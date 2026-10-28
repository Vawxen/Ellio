#!/usr/bin/env python3
"""
Audio Processing Agent for Ellio pipeline.
Handles audio extraction, enhancement, and mixing.
"""

import os
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent, ArtifactReference


class AudioAgent(BaseAgent):
    """Audio processing agent."""
    
    def __init__(self):
        super().__init__("audio-agent")
    
    def process(self, inputs, outputs, parameters):
        """
        Process audio from video file.
        
        Expected inputs:
        - video: Input video file
        
        Expected outputs:
        - audio: Extracted audio file
        """
        # Get input video path
        video_input = self.get_input_path(inputs, 'video')
        if not video_input:
            raise ValueError("Missing required input: video")
        
        # Get output audio path
        audio_output = self.get_output_path(outputs, 'audio')
        if not audio_output:
            raise ValueError("Missing required output: audio")
        
        # Extract audio using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', video_input,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM 16-bit little-endian
            '-ar', '44100',  # Sample rate
            '-ac', '2',  # Stereo
            audio_output,
            '-y'  # Overwrite output file
        ]
        
        self.logger.info(f"Extracting audio: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Audio extraction failed: {result.stderr}")
            raise RuntimeError(f"Audio extraction failed: {result.stderr}")
        
        # Validate output file exists and has content
        if not os.path.exists(audio_output) or os.path.getsize(audio_output) == 0:
            raise RuntimeError("Audio extraction produced empty or missing file")
        
        self.logger.info(f"Audio extracted successfully: {audio_output}")
        
        # Create output artifact reference
        output_artifact = ArtifactReference(
            artifact_type="audio",
            artifact_id=os.path.basename(audio_output),
            version="1.0",
            location=f"file://{os.path.abspath(audio_output)}",
            producer_stage=self.stage_id,
            validation_status="passed"
        )
        
        return [output_artifact]


if __name__ == "__main__":
    agent = AudioAgent()
    agent.run()