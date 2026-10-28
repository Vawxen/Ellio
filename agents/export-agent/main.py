#!/usr/bin/env python3
"""
Export/Render Agent for Ellio pipeline.
Handles final rendering and export to various formats.
"""

import os
import json
import subprocess
from pathlib import Path
from base_agent import BaseAgent, ArtifactReference


class ExportAgent(BaseAgent):
    """Export/render agent."""
    
    def __init__(self):
        super().__init__("export-agent")
    
    def process(self, inputs, outputs, parameters):
        """
        Render and export final video.
        
        Expected inputs:
        - video: Input video file (edited/composition)
        
        Expected outputs:
        - video: Final exported video file
        """
        # Get input video path
        video_input = self.get_input_path(inputs, 'video')
        if not video_input:
            raise ValueError("Missing required input: video")
        
        # Get output video path
        video_output = self.get_output_path(outputs, 'video')
        if not video_output:
            raise ValueError("Missing required output: video")
        
        # Get parameters for export
        # Format can be specified via extension or explicit format parameter
        output_format = parameters.get('format', None)
        if not output_format:
            # Try to infer from file extension
            _, ext = os.path.splitext(video_output)
            if ext:
                output_format = ext.lower().lstrip('.')
            else:
                output_format = 'mp4'  # Default to MP4
        
        # Quality preset
        quality = parameters.get('quality', 'medium')  # low, medium, high, lossless
        
        # Resolution parameters
        width = parameters.get('width', None)
        height = parameters.get('height', None)
        
        # Build ffmpeg command
        cmd = ['ffmpeg', '-i', video_input]
        
        # Add video filters if resolution specified
        vfilters = []
        if width and height:
            vfilters.append(f'scale={width}:{height}')
        elif width:
            vfilters.append(f'scale={width}:-2')
        elif height:
            vfilters.append(f'scale=-2:{height}')
        
        if vfilters:
            cmd.extend(['-vf', ','.join(vfilters)])
        
        # Set encoding parameters based on quality and format
        if output_format in ['mp4', 'mov', 'm4v']:
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'medium' if quality == 'medium' else ('veryfast' if quality == 'low' else 'slow'),
                '-crf', '23' if quality == 'medium' else ('28' if quality == 'low' else '18'),
                '-c:a', 'aac',
                '-b:a', '192k' if quality == 'high' else ('128k' if quality == 'medium' else '96k')
            ])
        elif output_format == 'webm':
            cmd.extend([
                '-c:v', 'libvpx-vp9',
                '-b:v', '0',
                '-crf', '30' if quality == 'medium' else ('35' if quality == 'low' else '25'),
                '-c:a', 'libopus',
                '-b:a', '128k' if quality == 'high' else ('96k' if quality == 'medium' else '64k')
            ])
        elif output_format == 'avi':
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'medium' if quality == 'medium' else ('veryfast' if quality == 'low' else 'slow'),
                '-crf', '23' if quality == 'medium' else ('28' if quality == 'low' else '18'),
                '-c:a', 'pcm_s16le' if quality == 'lossless' else 'aac',
                '-b:a', '192k' if quality == 'high' else ('128k' if quality == 'medium' else '96k')
            ])
        else:
            # Default to libx264/aac in mp4 container
            cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k'
            ])
        
        cmd.extend([
            video_output,
            '-y'  # Overwrite output file
        ])
        
        self.logger.info(f"Exporting video: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.logger.error(f"Export failed: {result.stderr}")
            raise RuntimeError(f"Export failed: {result.stderr}")
        
        # Validate output file exists and has content
        if not os.path.exists(video_output) or os.path.getsize(video_output) == 0:
            raise RuntimeError("Export produced empty or missing file")
        
        self.logger.info(f"Export completed successfully: {video_output}")
        
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
    agent = ExportAgent()
    agent.run()