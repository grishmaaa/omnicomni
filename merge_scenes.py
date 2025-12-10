#!/usr/bin/env python3
"""
Final Assembly - Merge Videos with Audio
Task 11: Audio-driven video assembly with looping

Strategy: "Audio is Master"
- Audio duration determines final video length
- Video loops to fill audio duration
- Proper codec settings for universal playback

Follows OmniComni patterns from generate_videos.py
"""

import argparse
import logging
import math
import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from collections import defaultdict

from src.core.ffmpeg_service import FFmpegService


# ============================================================================
# CONFIGURATION
# ============================================================================

# Output settings
DEFAULT_VIDEO_INPUT = "output/video/clips"
DEFAULT_AUDIO_INPUT = "output"  # Will look for {timestamp}_{topic}/2_audio/
DEFAULT_OUTPUT_BASE = "output/video/final"

# Encoding defaults
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
PIXEL_FORMAT = "yuv420p"  # Critical for compatibility


# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_duration(file_path: Path, ffmpeg_service: FFmpegService) -> float:
    """
    Get media file duration in seconds
    
    Args:
        file_path: Path to media file
        ffmpeg_service: FFmpeg service instance
        
    Returns:
        Duration in seconds
        
    Raises:
        RuntimeError: If file is corrupt or duration cannot be determined
    """
    try:
        metadata = ffmpeg_service.get_video_metadata(file_path)
        duration = metadata.get('duration', 0)
        
        if duration <= 0:
            raise RuntimeError(f"Invalid duration: {duration}")
        
        return duration
        
    except Exception as e:
        raise RuntimeError(f"Failed to get duration for {file_path}: {e}")


def merge_audio_video_with_loop(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    ffmpeg_service: FFmpegService
) -> Path:
    """
    Merge video and audio with video looping to match audio duration
    
    Strategy: "Audio is Master"
    - Get audio duration (audio_dur)
    - Get video duration (video_dur)
    - Calculate loops: ceil(audio_dur / video_dur)
    - Loop video to fill audio duration
    - Trim to exact audio duration
    
    Args:
        video_path: Input video (silent, from SVD)
        audio_path: Input audio (narration, from TTS)
        output_path: Output merged video
        ffmpeg_service: FFmpeg service instance
        
    Returns:
        Path to merged video
        
    Technical Notes:
    - Pixel Format (yuv420p):
      * CRITICAL for broad compatibility
      * Default ffmpeg output can be 4:4:4 which breaks on:
        - QuickTime (macOS)
        - Windows Media Player
        - Many mobile devices
      * yuv420p is the universal standard for H.264/MP4
    
    - Container Flags (+faststart):
      * Moves metadata to beginning of file
      * Enables progressive web streaming
      * Allows playback to start before full download
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")
    
    # Get durations
    video_dur = get_duration(video_path, ffmpeg_service)
    
    # For audio, we need special handling as it's MP3
    try:
        cmd = [
            ffmpeg_service.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        audio_dur = float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to get audio duration: {e}")
    
    logger.info(
        f"Merging: video={video_dur:.1f}s, audio={audio_dur:.1f}s → "
        f"output={audio_dur:.1f}s"
    )
    
    # Calculate loops needed
    n_loops = math.ceil(audio_dur / video_dur)
    logger.debug(f"Video will loop {n_loops} times")
    
    # Ensure output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Construct FFmpeg command with proper looping and trimming
        # 
        # Strategy:
        # 1. Use -stream_loop to repeat video input
        # 2. Use -t to trim to exact audio duration
        # 3. Map audio and video streams
        # 4. Encode with universal codecs
        
        cmd = [
            ffmpeg_service.ffmpeg_path,
            # Video input with looping
            "-stream_loop", str(n_loops - 1),  # -1 because first play doesn't count
            "-i", str(video_path),
            # Audio input
            "-i", str(audio_path),
            # Trim video to match audio duration
            "-t", str(audio_dur),
            # Video encoding
            "-c:v", VIDEO_CODEC,
            "-pix_fmt", PIXEL_FORMAT,  # CRITICAL: yuv420p for compatibility
            "-preset", "fast",  # Balance quality/speed
            "-crf", "23",  # Quality (18-28, lower = better)
            # Audio encoding
            "-c:a", AUDIO_CODEC,
            "-b:a", AUDIO_BITRATE,
            # Container optimization
            "-movflags", "+faststart",  # Enable web streaming
            # Sync
            "-shortest",  # Stop at shortest stream
            # Map streams
            "-map", "0:v:0",  # Video from first input
            "-map", "1:a:0",  # Audio from second input
            # Overwrite
            "-y",
            str(output_path)
        ]
        
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"✅ Merged: {output_path.name}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg merge failed: {e.stderr}")


def extract_scene_id(filename: str) -> Optional[int]:
    """Extract scene ID from filename"""
    match = re.search(r'scene[_-]?(\d+)', filename, re.IGNORECASE)
    return int(match.group(1)) if match else None


def find_audio_files(base_dir: Path, topic_slug: str) -> Dict[int, Path]:
    """
    Find audio files in pipeline_manager.py output structure
    
    Args:
        base_dir: Base output directory
        topic_slug: Topic slug to search for
        
    Returns:
        Dictionary mapping scene_id -> audio_path
    """
    audio_files = {}
    
    # Look for timestamped directories matching topic
    for project_dir in base_dir.glob(f"*_{topic_slug}"):
        audio_dir = project_dir / "2_audio"
        if not audio_dir.exists():
            continue
        
        for audio_file in audio_dir.glob("*.mp3"):
            scene_id = extract_scene_id(audio_file.stem)
            if scene_id is not None:
                audio_files[scene_id] = audio_file
                logger.debug(f"Found audio: scene {scene_id} -> {audio_file}")
    
    return audio_files


# ============================================================================
# MAIN ASSEMBLY LOGIC
# ============================================================================

def run_merge_pipeline(
    topic_slug: str,
    video_input_base: Path,
    audio_input_base: Path,
    output_base: Path,
    skip_existing: bool = True
) -> Dict:
    """
    Merge all scene videos with their audio narration
    
    Strategy: "Audio is Master"
    - Iterate through audio files (they determine what gets created)
    - Find matching video for each audio
    - Loop video to match audio duration
    - Create final synced videos
    
    Args:
        topic_slug: Topic identifier
        video_input_base: Base directory for videos
        audio_input_base: Base directory for audio (pipeline output)
        output_base: Where to save merged videos
        skip_existing: Skip if output exists
        
    Returns:
        Statistics dictionary
    """
    # Initialize FFmpeg service
    logger.info("Initializing FFmpeg service...")
    ffmpeg_service = FFmpegService()
    
    # Setup paths
    video_dir = video_input_base / topic_slug
    output_dir = output_base / topic_slug
    
    if not video_dir.exists():
        raise FileNotFoundError(f"Video directory not found: {video_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find audio files (AUDIO IS MASTER)
    logger.info(f"📁 Scanning audio files...")
    audio_files = find_audio_files(audio_input_base, topic_slug)
    
    if not audio_files:
        raise ValueError(f"No audio files found for topic: {topic_slug}")
    
    logger.info(f"✅ Found {len(audio_files)} audio files")
    
    # Statistics
    total_scenes = len(audio_files)
    successful = 0
    skipped = 0
    failed = 0
    
    logger.info(f"\n🎬 Merging {total_scenes} scenes")
    logger.info(f"📁 Output: {output_dir}\n")
    
    # Process each scene
    for scene_id in sorted(audio_files.keys()):
        audio_path = audio_files[scene_id]
        
        # Find corresponding video
        video_filename = f"scene_{scene_id:02d}.mp4"
        video_path = video_dir / video_filename
        
        # Output filename
        output_filename = f"scene_{scene_id:02d}_final.mp4"
        output_path = output_dir / output_filename
        
        # Skip if exists
        if skip_existing and output_path.exists():
            logger.info(f"⏭️  Scene {scene_id:02d}: Already exists, skipping")
            skipped += 1
            continue
        
        logger.info(f"{'='*70}")
        logger.info(f"Scene {scene_id:02d}/{total_scenes}")
        logger.info(f"{'='*70}")
        
        # Check if video exists
        if not video_path.exists():
            logger.warning(f"⚠️  Video not found: {video_path.name}")
            logger.warning(f"   Skipping scene {scene_id}")
            failed += 1
            continue
        
        logger.info(f"Video: {video_path.name}")
        logger.info(f"Audio: {audio_path.name}")
        
        try:
            # Merge with looping
            merge_audio_video_with_loop(
                video_path=video_path,
                audio_path=audio_path,
                output_path=output_path,
                ffmpeg_service=ffmpeg_service
            )
            
            # Check output
            size_mb = output_path.stat().st_size / 1e6
            logger.info(f"✅ Created: {output_path.name} ({size_mb:.2f}MB)")
            successful += 1
            
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            logger.warning("Continuing with next scene...")
            failed += 1
        
        logger.info("")  # Blank line
    
    # Statistics
    stats = {
        "total_scenes": total_scenes,
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "output_directory": str(output_dir)
    }
    
    return stats


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Merge scene videos with audio narration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge videos and audio for topic
  python merge_scenes.py --topic cyberpunk_tokyo_scenes
  
  # Custom paths
  python merge_scenes.py --topic my_topic --video-dir output/video/clips --audio-dir output
  
  # Force regenerate all
  python merge_scenes.py --topic topic --no-skip
        """
    )
    
    parser.add_argument(
        '--topic',
        required=True,
        help='Topic slug (must match folders in video/audio directories)'
    )
    
    parser.add_argument(
        '--video-dir',
        type=Path,
        default=DEFAULT_VIDEO_INPUT,
        help=f'Video input base directory (default: {DEFAULT_VIDEO_INPUT})'
    )
    
    parser.add_argument(
        '--audio-dir',
        type=Path,
        default=DEFAULT_AUDIO_INPUT,
        help=f'Audio input base directory (default: {DEFAULT_AUDIO_INPUT})'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=DEFAULT_OUTPUT_BASE,
        help=f'Output base directory (default: {DEFAULT_OUTPUT_BASE})'
    )
    
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Regenerate all videos (ignore existing)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎬" * 35)
    print(" " * 20 + "FINAL ASSEMBLY")
    print(" " * 10 + "Video + Audio Merge Pipeline")
    print("🎬" * 35 + "\n")
    
    try:
        # Run merge pipeline
        stats = run_merge_pipeline(
            topic_slug=args.topic,
            video_input_base=args.video_dir,
            audio_input_base=args.audio_dir,
            output_base=args.output,
            skip_existing=not args.no_skip
        )
        
        # Summary
        print("\n" + "="*70)
        print("ASSEMBLY COMPLETE")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   Total scenes:  {stats['total_scenes']}")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ⏭️  Skipped:    {stats['skipped']}")
        print(f"   ❌ Failed:     {stats['failed']}")
        print(f"\n📁 Final videos: {stats['output_directory']}")
        print("="*70 + "\n")
        
        if stats['successful'] > 0:
            print("✅ SUCCESS: Video assembly complete!")
            print("\n💡 Final videos ready for:")
            print("   - Direct playback")
            print("   - Upload to platforms")
            print("   - Further editing")
            sys.exit(0)
        else:
            print("❌ FAILED: No videos assembled")
            sys.exit(1)
            
    except FileNotFoundError as e:
        logger.error(f"\n❌ {e}")
        logger.info("\nMake sure you've run:")
        logger.info("  1. python generate_videos.py --topic <topic>")
        logger.info("  2. python pipeline_manager.py --topic <topic>")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Assembly cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Assembly failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
