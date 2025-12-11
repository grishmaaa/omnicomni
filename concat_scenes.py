#!/usr/bin/env python3
"""
Scene Concatenation - Task 12
Stitch all scene videos into single final video

Strategy: Filter Complex (Robust)
- Handles codec/timebase inconsistencies
- Re-encodes for guaranteed compatibility
- Adds professional fade in/out

Follows OmniComni patterns from merge_scenes.py
"""

import argparse
import logging
import re
import sys
import subprocess
from pathlib import Path
from typing import List

from src.core.ffmpeg_service import FFmpegService


# ============================================================================
# CONFIGURATION
# ============================================================================

# Input/Output defaults
DEFAULT_INPUT_BASE = "output/video/final"
DEFAULT_OUTPUT_BASE = "output/video/complete"

# Encoding settings
VIDEO_CODEC = "libx264"
VIDEO_PRESET = "medium"  # Balance quality/speed
VIDEO_CRF = "23"  # Quality (18-28, lower = better)
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
PIXEL_FORMAT = "yuv420p"

# Fade durations (seconds)
FADE_IN_DURATION = 1.0
FADE_OUT_DURATION = 1.0


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

def extract_scene_number(filename: str) -> int:
    """
    Extract scene number from filename
    
    Args:
        filename: e.g., "scene_01_final.mp4"
        
    Returns:
        Scene number as integer
        
    Critical: Uses regex to extract number for proper numerical sorting.
    String sorting would put scene_10 before scene_2!
    """
    match = re.search(r'scene[_-]?(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0  # Fallback for files without scene number


def get_sorted_clips(input_dir: Path) -> List[Path]:
    """
    Get scene clips sorted numerically
    
    Args:
        input_dir: Directory containing scene videos
        
    Returns:
        List of video paths sorted by scene number
        
    Raises:
        FileNotFoundError: If no clips found
        
    Technical Note:
    - Uses numerical sorting (1, 2, 3, ..., 10)
    - NOT string sorting ("scene_10" < "scene_2")
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Find all video files
    clips = list(input_dir.glob("scene_*.mp4"))
    
    if not clips:
        raise FileNotFoundError(f"No scene clips found in {input_dir}")
    
    # Sort numerically by scene number
    clips.sort(key=lambda p: extract_scene_number(p.name))
    
    logger.info(f"Found {len(clips)} clips:")
    for clip in clips:
        logger.info(f"  - {clip.name}")
    
    return clips


# ============================================================================
# CONCATENATION LOGIC
# ============================================================================

def concatenate_videos(
    clips: List[Path],
    output_path: Path,
    ffmpeg_service: FFmpegService
) -> Path:
    """
    Concatenate multiple videos into single file
    
    Uses Filter Complex method for maximum robustness.
    
    Args:
        clips: List of video paths (in order)
        output_path: Output video path
        ffmpeg_service: FFmpeg service instance
        
    Returns:
        Path to concatenated video
        
    Technical Decision: Filter Complex vs Concat Demuxer
    
    Concat Demuxer (NOT USED):
    - Faster (no re-encoding)
    - Fails if inputs have different:
      * Codecs
      * Resolutions  
      * Timebases
      * Pixel formats
    - Risk: "Non-monotonous DTS" errors
    
    Filter Complex (CHOSEN):
    - Slower (re-encodes everything)
    - Bulletproof: handles any input inconsistencies
    - Guarantees output compatibility
    - Allows effects (fades, transitions)
    
    Production Choice: Robustness > Speed
    Better to spend 2 minutes encoding than debug sync issues!
    
    Fade Effects:
    - 1s fade in at start (professional opening)
    - 1s fade out at end (clean closing)
    - No cross-fades between scenes (risk sync drift)
    """
    if not clips:
        raise ValueError("No clips provided for concatenation")
    
    # Pre-flight check: Ensure all clips have audio
    # Critical: Filter complex requires all inputs to have [0:a] mapping
    missing_audio = []
    for clip in clips:
        if not ffmpeg_service.has_audio_stream(clip):
            missing_audio.append(clip.name)
            logger.error(f"❌ Clip has NO audio stream: {clip.name}")
            
    if missing_audio:
        raise RuntimeError(
            f"Found {len(missing_audio)} clips without audio! "
            "Concatenation requires audio for all inputs.\n"
            "Please re-run: python merge_scenes.py --topic <topic> --no-skip"
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n🎬 Concatenating {len(clips)} clips...")
    logger.info(f"📁 Output: {output_path}\n")
    
    try:
        # Build filter complex
        # Strategy:
        # 1. Input all clips
        # 2. Concat video/audio streams
        # 3. Apply fade in/out
        # 4. Encode with standard settings
        
        # Build input arguments
        inputs = []
        for clip in clips:
            inputs.extend(["-i", str(clip)])
        
        # Build concat filter
        # Format: [0:v][0:a][1:v][1:a]...[N:v][N:a]concat=n=N:v=1:a=1[v][a]
        n_clips = len(clips)
        
        # Video/audio stream selectors
        stream_selectors = []
        for i in range(n_clips):
            stream_selectors.append(f"[{i}:v]")
            stream_selectors.append(f"[{i}:a]")
        
        # Concat filter
        concat_filter = (
            f"{''.join(stream_selectors)}"
            f"concat=n={n_clips}:v=1:a=1[vconcatenated][aconcatenated]"
        )
        
        # Add fade in/out to video
        # Fade in at start (first FADE_IN_DURATION seconds)
        # Fade out at end (last FADE_OUT_DURATION seconds)
        # Note: We need total duration for fade out calculation
        
        # Get total duration (sum of all clips)
        total_duration = 0.0
        for clip in clips:
            metadata = ffmpeg_service.get_video_metadata(clip)
            total_duration += metadata['duration']
        
        fade_out_start = total_duration - FADE_OUT_DURATION
        
        video_filter = (
            f"{concat_filter};"
            f"[vconcatenated]"
            f"fade=t=in:st=0:d={FADE_IN_DURATION},"
            f"fade=t=out:st={fade_out_start}:d={FADE_OUT_DURATION}"
            f"[vfinal]"
        )
        
        logger.info(f"Total duration: {total_duration:.1f}s")
        logger.info(f"Fade in: 0-{FADE_IN_DURATION}s")
        logger.info(f"Fade out: {fade_out_start:.1f}-{total_duration:.1f}s\n")
        
        # Build complete FFmpeg command
        cmd = [
            ffmpeg_service.ffmpeg_path,
            # Inputs
            *inputs,
            # Filter complex
            "-filter_complex", video_filter,
            # Map outputs
            "-map", "[vfinal]",
            "-map", "[aconcatenated]",
            # Video encoding
            "-c:v", VIDEO_CODEC,
            "-preset", VIDEO_PRESET,
            "-crf", VIDEO_CRF,
            "-pix_fmt", PIXEL_FORMAT,
            # Audio encoding
            "-c:a", AUDIO_CODEC,
            "-b:a", AUDIO_BITRATE,
            # Container optimization
            "-movflags", "+faststart",
            # Overwrite
            "-y",
            str(output_path)
        ]
        
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        # Run FFmpeg
        logger.info("Encoding final video (this may take a few minutes)...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"\n✅ Concatenation complete: {output_path}")
        
        # Validate output
        final_metadata = ffmpeg_service.get_video_metadata(output_path)
        output_size_mb = output_path.stat().st_size / 1e6
        
        logger.info(f"\n📊 Final Video:")
        logger.info(f"   Duration: {final_metadata['duration']:.1f}s")
        logger.info(f"   Resolution: {final_metadata['width']}x{final_metadata['height']}")
        logger.info(f"   Codec: {final_metadata['codec_name']}")
        logger.info(f"   FPS: {final_metadata['fps']}")
        logger.info(f"   Size: {output_size_mb:.2f}MB")
        
        return output_path
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg concatenation failed: {e.stderr}")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_concatenation(
    topic_slug: str,
    input_base: Path,
    output_base: Path
) -> Path:
    """
    Concatenate all scene videos for a topic
    
    Args:
        topic_slug: Topic identifier
        input_base: Base directory for scene videos
        output_base: Base directory for output
        
    Returns:
        Path to final concatenated video
    """
    # Initialize FFmpeg
    logger.info("Initializing FFmpeg service...")
    ffmpeg_service = FFmpegService()
    
    # Setup paths
    input_dir = input_base / topic_slug
    output_dir = output_base
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_filename = f"{topic_slug}_complete.mp4"
    output_path = output_dir / output_filename
    
    # Get sorted clips
    logger.info(f"📁 Scanning: {input_dir}")
    clips = get_sorted_clips(input_dir)
    
    # Concatenate
    final_video = concatenate_videos(
        clips=clips,
        output_path=output_path,
        ffmpeg_service=ffmpeg_service
    )
    
    return final_video


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Concatenate scene videos into final complete video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Concatenate scenes for topic
  python concat_scenes.py --topic cyberpunk_tokyo_scenes
  
  # Custom paths
  python concat_scenes.py --topic my_topic --input output/video/final --output output/final_videos

End-to-End Usage:
  1. python pipeline_manager.py --topic "My Topic"
  2. python generate_images.py --input output/{timestamp}_my_topic/1_scripts/my_topic_scenes.json
  3. python generate_videos.py --topic my_topic_scenes
  4. python merge_scenes.py --topic my_topic_scenes
  5. python concat_scenes.py --topic my_topic_scenes  ← This script
  
  Result: output/video/complete/my_topic_scenes_complete.mp4
        """
    )
    
    parser.add_argument(
        '--topic',
        required=True,
        help='Topic slug (must match folder in input directory)'
    )
    
    parser.add_argument(
        '--input',
        type=Path,
        default=DEFAULT_INPUT_BASE,
        help=f'Input base directory (default: {DEFAULT_INPUT_BASE})'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=DEFAULT_OUTPUT_BASE,
        help=f'Output base directory (default: {DEFAULT_OUTPUT_BASE})'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎬" * 35)
    print(" " * 20 + "SCENE CONCATENATION")
    print(" " * 15 + "Final Video Assembly")
    print("🎬" * 35 + "\n")
    
    try:
        # Run concatenation
        final_video = run_concatenation(
            topic_slug=args.topic,
            input_base=args.input,
            output_base=args.output
        )
        
        # Success
        print("\n" + "="*70)
        print("CONCATENATION COMPLETE")
        print("="*70)
        print(f"\n✅ Final video: {final_video}")
        print(f"\n💡 Ready for:")
        print("   - Direct playback")
        print("   - Upload to YouTube/TikTok/Twitter")
        print("   - Distribution")
        print("="*70 + "\n")
        
        sys.exit(0)
        
    except FileNotFoundError as e:
        logger.error(f"\n❌ {e}")
        logger.info("\nMake sure you've run:")
        logger.info("  python merge_scenes.py --topic <topic>")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Concatenation cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Concatenation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
