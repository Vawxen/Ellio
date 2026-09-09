#!/usr/bin/env python3
"""
Subtitle Generation Agent for Ellio Pipeline.
Generates subtitle files (SRT format) from translated transcripts.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from base_agent import BaseAgent, main


class SubtitleGenerationAgent(BaseAgent):
    """Agent for generating subtitle files from transcripts."""
    
    def __init__(self):
        super().__init__("subtitle-generation-agent")
    
    def run(self) -> int:
        """Execute the subtitle generation stage."""
        self.log("Starting subtitle generation")
        
        # Get input transcript location
        input_location = self.get_input_location(0)
        if not input_location:
            self.log("No input transcript provided", "ERROR")
            return 1
        
        self.log(f"Input transcript: {input_location}")
        
        # Get output location
        output_location = self._get_output_location()
        if not output_location:
            self.log("No output location specified", "ERROR")
            return 1
        
        self.log(f"Output subtitles: {output_location}")
        
        # Resolve file paths
        src_path = self.resolve_file_path(input_location)
        dst_path = self.resolve_file_path(output_location)
        
        if not src_path or not dst_path:
            self.log("Invalid file URIs", "ERROR")
            return 1
        
        if not src_path.exists():
            self.log(f"Source transcript does not exist: {src_path}", "ERROR")
            return 1
        
        # Read input transcript
        try:
            with open(src_path, 'r', encoding='utf-8') as f:
                transcript = json.load(f)
        except Exception as e:
            self.log(f"Failed to read input transcript: {e}", "ERROR")
            return 1
        
        # Generate SRT subtitles
        srt_content = self._generate_srt(transcript)
        
        # Write SRT file
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            self.log("Subtitle generation completed successfully")
            return 0
        except Exception as e:
            self.log(f"Failed to write subtitles: {e}", "ERROR")
            return 1
    
    def _get_output_location(self) -> Optional[str]:
        """Get the output location from environment."""
        for key, value in os.environ.items():
            if key.startswith("OUTPUT_") and key.endswith("_LOCATION"):
                return value
        return self.parameters.get("output_location")
    
    def _generate_srt(self, transcript: dict) -> str:
        """Generate SRT format subtitles from transcript."""
        srt_lines = []
        
        for segment in transcript.get("segments", []):
            segment_id = segment.get("id", 0)
            start = segment.get("start", 0.0)
            end = segment.get("end", 0.0)
            text = segment.get("text", "")
            
            # Format timestamps as SRT (HH:MM:SS,mmm)
            start_str = self._format_srt_time(start)
            end_str = self._format_srt_time(end)
            
            srt_lines.append(str(segment_id + 1))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(text)
            srt_lines.append("")  # Empty line between subtitles
        
        return "\n".join(srt_lines)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def create_agent() -> BaseAgent:
    return SubtitleGenerationAgent()


if __name__ == "__main__":
    main()