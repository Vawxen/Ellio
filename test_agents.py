#!/usr/bin/env python3
"""
Test script for Ellio agents.
Verifies that agents can be invoked and produce expected outputs.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from ingest_agent.main import IngestAgent
from transcription_agent.main import TranscriptionAgent
from translation_agent.main import TranslationAgent
from subtitle_generation_agent.main import SubtitleGenerationAgent
from base_agent import ArtifactReference


def create_test_video():
    """Create a minimal test video file."""
    test_dir = Path(tempfile.gettempdir()) / "ellio_test"
    test_dir.mkdir(exist_ok=True)
    
    video_path = test_dir / "test_video.mp4"
    
    # Create a minimal fake video file (just some bytes)
    if not video_path.exists():
        with open(video_path, 'wb') as f:
            f.write(b"fake video content for testing")
    
    return video_path


def test_ingest_agent():
    """Test the ingest agent."""
    print("Testing Ingest Agent...")
    
    video_path = create_test_video()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "ingested_video.mp4"
        
        # Set up environment
        os.environ["INPUT_0_TYPE"] = "video"
        os.environ["INPUT_0_ID"] = "source-video"
        os.environ["INPUT_0_VERSION"] = "1.0.0"
        os.environ["INPUT_0_LOCATION"] = f"file://{video_path}"
        os.environ["OUTPUT_0_LOCATION"] = f"file://{output_path}"
        os.environ["STAGE_STAGEID"] = "ingest"
        
        agent = IngestAgent()
        exit_code = agent.run()
        
        # Clean up environment
        for key in list(os.environ.keys()):
            if key.startswith(("INPUT_", "OUTPUT_", "STAGE_", "PARAM_")):
                del os.environ[key]
        
        assert exit_code == 0, f"Ingest agent failed with exit code {exit_code}"
        assert output_path.exists(), "Output file was not created"
        assert output_path.stat().st_size > 0, "Output file is empty"
        
        print("  ✓ Ingest agent test passed")
        return True


def test_transcription_agent():
    """Test the transcription agent."""
    print("Testing Transcription Agent...")
    
    video_path = create_test_video()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "transcript.json"
        
        # Set up environment
        os.environ["INPUT_0_TYPE"] = "video"
        os.environ["INPUT_0_ID"] = "ingested-video"
        os.environ["INPUT_0_VERSION"] = "1.0.0"
        os.environ["INPUT_0_LOCATION"] = f"file://{video_path}"
        os.environ["OUTPUT_0_LOCATION"] = f"file://{output_path}"
        os.environ["STAGE_STAGEID"] = "transcription"
        
        agent = TranscriptionAgent()
        exit_code = agent.run()
        
        # Clean up environment
        for key in list(os.environ.keys()):
            if key.startswith(("INPUT_", "OUTPUT_", "STAGE_", "PARAM_")):
                del os.environ[key]
        
        assert exit_code == 0, f"Transcription agent failed with exit code {exit_code}"
        assert output_path.exists(), "Transcript file was not created"
        
        # Verify transcript structure
        with open(output_path, 'r') as f:
            transcript = json.load(f)
        
        assert "language" in transcript
        assert "duration" in transcript
        assert "segments" in transcript
        assert isinstance(transcript["segments"], list)
        assert len(transcript["segments"]) > 0
        
        print("  ✓ Transcription agent test passed")
        return True


def test_translation_agent():
    """Test the translation agent."""
    print("Testing Translation Agent...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test transcript
        input_path = Path(tmpdir) / "transcript.json"
        output_path = Path(tmpdir) / "translated_transcript.json"
        
        test_transcript = {
            "language": "en",
            "duration": 10.0,
            "segments": [
                {"id": 0, "start": 0.0, "end": 5.0, "text": "Hello world", "confidence": 0.95},
                {"id": 1, "start": 5.0, "end": 10.0, "text": "This is a test", "confidence": 0.90}
            ]
        }
        
        with open(input_path, 'w') as f:
            json.dump(test_transcript, f)
        
        # Set up environment
        os.environ["INPUT_0_TYPE"] = "transcript"
        os.environ["INPUT_0_ID"] = "video-transcript"
        os.environ["INPUT_0_VERSION"] = "1.0.0"
        os.environ["INPUT_0_LOCATION"] = f"file://{input_path}"
        os.environ["OUTPUT_0_LOCATION"] = f"file://{output_path}"
        os.environ["STAGE_STAGEID"] = "translation"
        os.environ["PARAM_TARGET_LANGUAGE"] = "es"
        
        agent = TranslationAgent()
        exit_code = agent.run()
        
        # Clean up environment
        for key in list(os.environ.keys()):
            if key.startswith(("INPUT_", "OUTPUT_", "STAGE_", "PARAM_")):
                del os.environ[key]
        
        assert exit_code == 0, f"Translation agent failed with exit code {exit_code}"
        assert output_path.exists(), "Translation file was not created"
        
        # Verify translation structure
        with open(output_path, 'r') as f:
            translation = json.load(f)
        
        assert translation["language"] == "es"
        assert translation["translated_from"] == "en"
        assert "segments" in translation
        assert len(translation["segments"]) == 2
        
        print("  ✓ Translation agent test passed")
        return True


def test_subtitle_generation_agent():
    """Test the subtitle generation agent."""
    print("Testing Subtitle Generation Agent...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test translated transcript
        input_path = Path(tmpdir) / "translated_transcript.json"
        output_path = Path(tmpdir) / "subtitles.srt"
        
        test_transcript = {
            "language": "es",
            "duration": 10.0,
            "segments": [
                {"id": 0, "start": 0.0, "end": 5.0, "text": "[ES] Hello world"},
                {"id": 1, "start": 5.0, "end": 10.0, "text": "[ES] This is a test"}
            ]
        }
        
        with open(input_path, 'w') as f:
            json.dump(test_transcript, f)
        
        # Set up environment
        os.environ["INPUT_0_TYPE"] = "translated-transcript"
        os.environ["INPUT_0_ID"] = "translated-transcript"
        os.environ["INPUT_0_VERSION"] = "1.0.0"
        os.environ["INPUT_0_LOCATION"] = f"file://{input_path}"
        os.environ["OUTPUT_0_LOCATION"] = f"file://{output_path}"
        os.environ["STAGE_STAGEID"] = "subtitle-generation"
        
        agent = SubtitleGenerationAgent()
        exit_code = agent.run()
        
        # Clean up environment
        for key in list(os.environ.keys()):
            if key.startswith(("INPUT_", "OUTPUT_", "STAGE_", "PARAM_")):
                del os.environ[key]
        
        assert exit_code == 0, f"Subtitle agent failed with exit code {exit_code}"
        assert output_path.exists(), "Subtitle file was not created"
        
        # Verify SRT format
        with open(output_path, 'r') as f:
            srt_content = f.read()
        
        assert "1" in srt_content  # First subtitle index
        assert "2" in srt_content  # Second subtitle index
        assert "-->" in srt_content  # Time separator
        assert "[ES] Hello world" in srt_content
        assert "[ES] This is a test" in srt_content
        
        print("  ✓ Subtitle generation agent test passed")
        return True


def run_all_tests():
    """Run all agent tests."""
    print("Running Ellio Agent Tests...")
    print("=" * 50)
    
    try:
        test_ingest_agent()
        test_transcription_agent()
        test_translation_agent()
        test_subtitle_generation_agent()
        
        print("=" * 50)
        print("All agent tests passed! ✓")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)