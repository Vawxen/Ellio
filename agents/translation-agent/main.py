#!/usr/bin/env python3
"""
Translation Agent for Ellio Pipeline.
Handles translation of transcript text to target language.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from base_agent import BaseAgent, main


class TranslationAgent(BaseAgent):
    """Agent for translating transcripts."""
    
    def __init__(self):
        super().__init__("translation-agent")
    
    def run(self) -> int:
        """Execute the translation stage."""
        self.log("Starting translation")
        
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
        
        self.log(f"Output translation: {output_location}")
        
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
        
        # Get target language from parameters
        target_language = self.parameters.get("target_language", "es")
        
        # Translate the transcript
        translated_transcript = self._translate_transcript(transcript, target_language)
        
        # Write translated transcript
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dst_path, 'w', encoding='utf-8') as f:
                json.dump(translated_transcript, f, indent=2, ensure_ascii=False)
            
            self.log(f"Translation to {target_language} completed successfully")
            return 0
        except Exception as e:
            self.log(f"Failed to write translation: {e}", "ERROR")
            return 1
    
    def _get_output_location(self) -> Optional[str]:
        """Get the output location from environment."""
        for key, value in os.environ.items():
            if key.startswith("OUTPUT_") and key.endswith("_LOCATION"):
                return value
        return self.parameters.get("output_location")
    
    def _translate_transcript(self, transcript: dict, target_language: str) -> dict:
        """Translate transcript segments. For MVP, this is a mock translation."""
        translated = transcript.copy()
        translated["language"] = target_language
        translated["translated_from"] = transcript.get("language", "en")
        translated["translation_metadata"] = {
            "model": "mock-translation-v1",
            "translated_at": datetime.utcnow().isoformat() + "Z",
            "agent": "translation-agent"
        }
        
        # Translate each segment (mock translation)
        translated_segments = []
        for segment in transcript.get("segments", []):
            translated_segment = segment.copy()
            # Mock translation: add language prefix
            original_text = segment.get("text", "")
            translated_segment["text"] = f"[{target_language.upper()}] {original_text}"
            translated_segment["original_text"] = original_text
            translated_segments.append(translated_segment)
        
        translated["segments"] = translated_segments
        return translated


def create_agent() -> BaseAgent:
    return TranslationAgent()


if __name__ == "__main__":
    main()