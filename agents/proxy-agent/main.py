#!/usr/bin/env python3
"""
Proxy Generation Agent for Ellio pipeline.
Generates low-resolution proxy files for easier editing.
"""

import os
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent, ArtifactReference


class ProxyAgent(BaseAgent):
    """Proxy generation agent."""
    
    def __init__(self):
        super().__init__("proxy-agent")
    
    def process(self, inputs, outputs, parameters):
        """
        Generate proxy video file.
        
        Expected inputs:
        - video: Input video file
        
        Expected outputs:
        - proxy: Low-resolution proxy video file
        """
        # Get input video path
        video_input = self.get_input_path(inputs, 'video')
        if not video_input:
            raise ValueError("Missing required input: video")
        
        # Get output proxy path
        proxy_output = self.get_output_path(outputs, 'proxy')
        if not proxy_output:
            raise ValueError("Missing required output: proxy")
        
        # Get parameters for proxy generation
        # Default to 720p height, maintain aspect ratio
        height = parameters.get('height', 720)
        # Optional: specify video bitrate for proxy
        video_bitrate = parameters.get('video_bitrate', '1500k')
        # Optional: specify audio bitrate for proxy
        audio_bitrate = parameters.get('audio_bitrate', '128k')
        
        # Build ffmpeg command to generate proxy
        cmd = [
            'ffmpeg',
            '-i', video_input,
            '-vf', f'scale=-2:{height}',  # Maintain aspect ratio, height specified
            '-c:v', 'libx264',
            '-preset', 'veryfast',  # Faster encoding for proxies
            '-b:v', video_bitrate,
            '-c:a', 'aac',
            '-b:a', audio_bitrate,
            proxy_output,
            '-y'  # Overwrite output file
        ]
        
        self.logger.info(f"Generating proxy: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Proxy generation failed: {result.stderr}")
            raise RuntimeError(f"Proxy generation failed: {result.stderr}")
        
        # Validate output file exists and has content
        if not os.path.exists(proxy_output) or os.path.getsize(proxy_output) == 0:
            raise RuntimeError("Proxy generation produced empty or missing file")
        
        self.logger.info(f"Proxy generated successfully: {proxy_output}")
        
        # Create output artifact reference
        output_artifact = ArtifactReference(
            artifact_type="proxy",
            artifact_id=os.path.basename(proxy_output),
            version="1.0",
            location=f"file://{os.path.abspath(proxy_output)}",
            producer_stage=self.stage_id,
            validation_status="passed"
        )
        
        return [output_artifact]


if __name__ == "__main__":
    agent = ProxyAgent()
    agent.run()