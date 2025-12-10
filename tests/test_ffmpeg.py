#!/usr/bin/env python3
"""
FFmpeg Sanity Check
Validates FFmpeg installation and capabilities

Run this before using video assembly features.
"""

import sys
import json
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.ffmpeg_service import FFmpegService
from src.core.exceptions import ConfigurationError


def main():
    """Run FFmpeg environment validation"""
    
    print("\n" + "🎬" * 35)
    print(" " * 15 + "FFMPEG SANITY CHECK")
    print(" " * 10 + "Environment Validation")
    print("🎬" * 35 + "\n")
    
    try:
        # Step 1: Initialize service (validates binaries)
        print("Step 1: Checking for FFmpeg binaries...")
        service = FFmpegService()
        print(f"✅ FFmpeg found: {service.ffmpeg_path}")
        print(f"✅ FFprobe found: {service.ffprobe_path}\n")
        
        # Step 2: Generate test video
        print("Step 2: Generating synthetic test video...")
        test_video = Path("test_output_ffmpeg.mp4")
        
        service.generate_test_video(
            output_path=test_video,
            duration=3,
            width=640,
            height=480
        )
        print(f"✅ Test video created: {test_video}")
        print(f"   Size: {test_video.stat().st_size / 1e6:.2f}MB\n")
        
        # Step 3: Extract metadata
        print("Step 3: Testing metadata extraction...")
        metadata = service.get_video_metadata(test_video)
        print("✅ Metadata extracted:")
        print(json.dumps(metadata, indent=2))
        print()
        
        # Step 4: Extract audio
        print("Step 4: Testing audio extraction...")
        test_audio = Path("test_audio_ffmpeg.mp3")
        
        service.extract_audio(
            input_path=test_video,
            output_path=test_audio
        )
        print(f"✅ Audio extracted: {test_audio}")
        print(f"   Size: {test_audio.stat().st_size / 1e6:.2f}MB\n")
        
        # Step 5: Test merge
        print("Step 5: Testing video+audio merge...")
        test_merged = Path("test_merged_ffmpeg.mp4")
        
        service.merge_video_audio(
            video_path=test_video,
            audio_path=test_audio,
            output_path=test_merged
        )
        print(f"✅ Merge successful: {test_merged}")
        print(f"   Size: {test_merged.stat().st_size / 1e6:.2f}MB\n")
        
        # Summary
        print("=" * 70)
        print("✅ SUCCESS: FFmpeg is correctly configured!")
        print("=" * 70)
        print("\nYou can now use:")
        print("  - Video metadata extraction")
        print("  - Audio extraction")
        print("  - Video+audio merging")
        print("\nTest files created:")
        print(f"  - {test_video}")
        print(f"  - {test_audio}")
        print(f"  - {test_merged}")
        print("\nCleanup (optional):")
        print("  rm test_*_ffmpeg.mp*")
        print()
        
        sys.exit(0)
        
    except ConfigurationError as e:
        print(f"\n❌ CONFIGURATION ERROR:\n{e}\n")
        print("Please install FFmpeg and try again.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
