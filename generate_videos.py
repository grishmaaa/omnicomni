#!/usr/bin/env python3
"""
Batch Video Generation - Task 9
Converts scene images to animated MP4 videos using SVD

Follows OmniComni patterns from generate_audio.py and generate_images.py.
Critical: Output filenames align with audio for final merge.

Architecture:
- Reads images from generate_images.py output
- Generates videos with synced filenames
- Supports resume (skips existing videos)
- Error resilient (continues on individual failures)
"""

import argparse
import logging
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Dict
from collections import defaultdict

from src.video.svd_client import VideoGenerator, VideoGenerationError
from src.core.gpu_manager import log_vram_stats, force_cleanup


# ============================================================================
# CONFIGURATION
# ============================================================================

# Video generation defaults
DEFAULT_FPS = 6  # SVD produces 25 frames: 25/6 ≈ 4.2s per clip
DEFAULT_MOTION_BUCKET = 127  # Balanced motion (1-255 scale)
DEFAULT_NOISE_AUG = 0.1  # Slight variation from source
DEFAULT_NUM_FRAMES = 25  # Standard SVD output

# Output directories
DEFAULT_INPUT_BASE = "output/images"
DEFAULT_OUTPUT_BASE = "output/video/clips"


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

def sanitize_slug(text: str) -> str:
    """Create safe directory name"""
    import re
    safe = re.sub(r'[^\w\s-]', '', text)
    safe = re.sub(r'[\s]+', '_', safe)
    return safe[:50].strip('_').lower()


def extract_scene_id(filename: str) -> Optional[int]:
    """
    Extract scene ID from filename
    
    Args:
        filename: e.g., "scene_01_var_01.png"
        
    Returns:
        Scene ID (1) or None
    """
    match = re.search(r'scene_(\d+)', filename)
    return int(match.group(1)) if match else None


def group_images_by_scene(image_dir: Path) -> Dict[int, List[Path]]:
    """
    Group image files by scene ID
    
    Args:
        image_dir: Directory containing scene images
        
    Returns:
        Dictionary mapping scene_id -> list of image paths
        
    Example:
        {
            1: [scene_01_var_01.png, scene_01_var_02.png],
            2: [scene_02_var_01.png]
        }
    """
    scenes = defaultdict(list)
    
    for img_path in sorted(image_dir.glob("scene_*.png")):
        scene_id = extract_scene_id(img_path.name)
        if scene_id is not None:
            scenes[scene_id].append(img_path)
    
    return dict(scenes)


def select_best_image(scene_images: List[Path]) -> Path:
    """
    Select best image from variations
    
    Args:
        scene_images: List of image paths for a scene
        
    Returns:
        Selected image path
        
    TODO: Future enhancement - use aesthetic scorer model
    (e.g., LAION aesthetic predictor) to automatically
    choose highest quality variation.
    
    Current implementation: Return first variant (var_01)
    which is consistent and reproducible.
    """
    # Sort to ensure consistent selection (var_01 first)
    sorted_images = sorted(scene_images)
    
    logger.debug(f"Selecting from {len(sorted_images)} variations: {sorted_images[0].name}")
    return sorted_images[0]


# ============================================================================
# MAIN GENERATION LOGIC
# ============================================================================

def generate_videos_for_topic(
    topic_slug: str,
    input_base: Path,
    output_base: Path,
    fps: int = DEFAULT_FPS,
    motion_bucket: int = DEFAULT_MOTION_BUCKET,
    skip_existing: bool = True
) -> Dict:
    """
    Generate videos for all scenes
    
    Args:
        topic_slug: Topic identifier
        input_base: Base input directory
        output_base: Base output directory
        fps: Video framerate (default 6)
        motion_bucket: Motion intensity (default 127)
        skip_existing: Skip if video exists (resume capability)
        
    Returns:
        Statistics dictionary
        
    Framerate Math:
    - SVD generates 25 frames
    - At 6 FPS: 25/6 ≈ 4.2 seconds per clip
    - At 7 FPS: 25/7 ≈ 3.6 seconds per clip
    - Trade-off: Lower FPS = smoother but longer videos
    
    Filename Mapping (CRITICAL for audio sync):
    - Input:  scene_01_var_01.png
    - Output: scene_01.mp4
    - Matches audio: scene_01.mp3 (from generate_audio.py)
    - Allows FFmpeg merge: ffmpeg -i scene_01.mp4 -i scene_01.mp3
    """
    # Setup directories
    input_dir = input_base / topic_slug
    output_dir = output_base / topic_slug
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Group images by scene
    logger.info(f"📁 Scanning images: {input_dir}")
    scenes = group_images_by_scene(input_dir)
    
    if not scenes:
        raise ValueError(f"No scene images found in {input_dir}")
    
    logger.info(f"✅ Found {len(scenes)} scenes")
    
    # Initialize video generator
    logger.info("\n🎬 Initializing SVD generator...")
    log_vram_stats("Before SVD load")
    
    generator = VideoGenerator()
    
    log_vram_stats("After SVD load")
    
    # Track statistics
    total_scenes = len(scenes)
    successful = 0
    skipped = 0
    failed = 0
    
    logger.info(f"\n🎥 Generating videos ({fps} FPS, motion={motion_bucket})")
    logger.info(f"📁 Output: {output_dir}\n")
    
    # Process each scene
    for scene_id in sorted(scenes.keys()):
        scene_images = scenes[scene_id]
        
        # Create output filename (CRITICAL: matches audio naming)
        output_filename = f"scene_{scene_id:02d}.mp4"
        output_path = output_dir / output_filename
        
        # Skip if exists (resume capability)
        if skip_existing and output_path.exists():
            logger.info(f"⏭️  Scene {scene_id:02d}: Already exists, skipping")
            skipped += 1
            continue
        
        logger.info(f"{'='*70}")
        logger.info(f"Scene {scene_id:02d}/{total_scenes}")
        logger.info(f"{'='*70}")
        
        # Select best image
        best_image = select_best_image(scene_images)
        logger.info(f"Selected image: {best_image.name}")
        
        try:
            # Generate video
            start_time = time.time()
            
            video_path = generator.generate_clip(
                image_path=best_image,
                output_path=output_path,
                motion_bucket_id=motion_bucket,
                num_frames=DEFAULT_NUM_FRAMES,
                fps=fps,
                seed=42 + scene_id  # Reproducible but varied per scene
            )
            
            gen_time = time.time() - start_time
            
            # Success
            size_mb = video_path.stat().st_size / 1e6
            logger.info(f"✅ Generated in {gen_time:.1f}s ({size_mb:.2f}MB)")
            successful += 1
            
        except VideoGenerationError as e:
            # Log error but continue (error resilience)
            logger.error(f"❌ Failed to generate video: {e}")
            logger.warning("Continuing with next scene...")
            failed += 1
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            logger.warning("Continuing with next scene...")
            failed += 1
        
        logger.info("")  # Blank line between scenes
    
    # Cleanup
    generator.unload()
    force_cleanup()
    log_vram_stats("After cleanup")
    
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
        description="Generate videos from scene images using SVD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From topic slug
  python generate_videos.py --topic cyberpunk_tokyo
  
  # Custom input/output
  python generate_videos.py --topic my_topic --input output/images --output output/videos
  
  # Custom FPS and motion
  python generate_videos.py --topic topic --fps 7 --motion 150
  
  # Regenerate all (no skip)
  python generate_videos.py --topic topic --no-skip
        """
    )
    
    parser.add_argument(
        '--topic',
        required=True,
        help='Topic slug (matches folder name in output/images/)'
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
    
    parser.add_argument(
        '--fps',
        type=int,
        default=DEFAULT_FPS,
        help=f'Video FPS (default: {DEFAULT_FPS})'
    )
    
    parser.add_argument(
        '--motion',
        type=int,
        default=DEFAULT_MOTION_BUCKET,
        help=f'Motion bucket ID 1-255 (default: {DEFAULT_MOTION_BUCKET})'
    )
    
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Regenerate all videos (ignore existing)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎬" * 35)
    print(" " * 20 + "VIDEO GENERATOR")
    print(" " * 10 + "Batch Image-to-Video Pipeline")
    print("🎬" * 35 + "\n")
    
    try:
        # Generate videos
        stats = generate_videos_for_topic(
            topic_slug=args.topic,
            input_base=args.input,
            output_base=args.output,
            fps=args.fps,
            motion_bucket=args.motion,
            skip_existing=not args.no_skip
        )
        
        # Summary
        print("\n" + "="*70)
        print("GENERATION COMPLETE")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   Total scenes:  {stats['total_scenes']}")
        print(f"   ✅ Successful: {stats['successful']}")
        print(f"   ⏭️  Skipped:    {stats['skipped']}")
        print(f"   ❌ Failed:     {stats['failed']}")
        print(f"\n📁 Videos saved to: {stats['output_directory']}")
        
        if stats['successful'] > 0:
            print("\n💡 Next step: Merge with audio using FFmpeg")
            print(f"   Example: ffmpeg -i scene_01.mp4 -i scene_01.mp3 -c copy final.mp4")
        
        print("="*70 + "\n")
        
        # Exit code
        if stats['successful'] > 0:
            print("✅ SUCCESS: Video generation complete!")
            sys.exit(0)
        else:
            print("❌ FAILED: No videos generated")
            sys.exit(1)
            
    except FileNotFoundError as e:
        logger.error(f"\n❌ {e}")
        logger.info(f"\nMake sure you've run:")
        logger.info(f"  python generate_images.py --input <scenes.json>")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Generation cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
