#!/usr/bin/env python3
"""
SVD Video Generation Test
Tests Stable Video Diffusion image-to-video pipeline

Usage:
    python tests/test_svd.py --image path/to/image.png
    python tests/test_svd.py --image path/to/image.png --output my_video.mp4
"""

import argparse
import logging
import sys
import time
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.video.svd_client import VideoGenerator, VideoGenerationError
from src.core.gpu_manager import log_vram_stats


# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Test image (if none provided)
DEFAULT_TEST_IMAGE_URL = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/svd/rocket.png"


# ============================================================================
# UTILITIES
# ============================================================================

def download_test_image(url: str, output_path: Path):
    """
    Download test image from URL
    
    Args:
        url: Image URL
        output_path: Where to save
    """
    logger.info(f"Downloading test image from HuggingFace...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        image.save(output_path)
        
        logger.info(f"✅ Downloaded: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to download test image: {e}")
        raise


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_basic_generation(image_path: Path, output_path: Path):
    """
    Test basic video generation
    
    Args:
        image_path: Input image
        output_path: Output video
    """
    logger.info("\n" + "="*70)
    logger.info("TEST: Basic Video Generation")
    logger.info("="*70)
    
    # Check input exists
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Log VRAM before
    log_vram_stats("Before SVD load")
    
    # Initialize generator
    start_time = time.time()
    generator = VideoGenerator()
    load_time = time.time() - start_time
    
    logger.info(f"✅ Model loaded in {load_time:.1f}s")
    log_vram_stats("After SVD load")
    
    # Generate video
    logger.info(f"\nGenerating video from: {image_path}")
    gen_start = time.time()
    
    video_path = generator.generate_clip(
        image_path=image_path,
        output_path=output_path,
        num_frames=25,
        fps=6,
        seed=42  # Reproducible
    )
    
    gen_time = time.time() - gen_start
    
    # Results
    logger.info("\n" + "="*70)
    logger.info("RESULTS")
    logger.info("="*70)
    logger.info(f"✅ Video generated: {video_path}")
    logger.info(f"   Generation time: {gen_time:.1f}s")
    logger.info(f"   Total time: {load_time + gen_time:.1f}s")
    
    # Check output
    if video_path.exists():
        size_mb = video_path.stat().st_size / 1e6
        logger.info(f"   File size: {size_mb:.2f}MB")
        logger.info(f"\n💡 Play video: mpv {video_path}")
    else:
        raise FileNotFoundError("Video file not created!")
    
    # Cleanup
    generator.unload()
    log_vram_stats("After cleanup")


def test_motion_variations(image_path: Path, output_dir: Path):
    """
    Test different motion settings
    
    Args:
        image_path: Input image
        output_dir: Output directory
    """
    logger.info("\n" + "="*70)
    logger.info("TEST: Motion Variations")
    logger.info("="*70)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Test different motion levels
    motion_levels = [
        (50, "low_motion"),
        (127, "medium_motion"),
        (200, "high_motion")
    ]
    
    generator = VideoGenerator()
    
    for motion_id, name in motion_levels:
        logger.info(f"\nGenerating {name} (motion_bucket_id={motion_id})...")
        
        output_path = output_dir / f"test_{name}.mp4"
        
        try:
            generator.generate_clip(
                image_path=image_path,
                output_path=output_path,
                motion_bucket_id=motion_id,
                num_frames=14,  # Shorter for quick test
                fps=7,
                seed=42
            )
            logger.info(f"✅ {name}: {output_path}")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}")
    
    generator.unload()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="Test SVD video generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default test image
  python tests/test_svd.py
  
  # Use custom image
  python tests/test_svd.py --image my_scene.png
  
  # Custom output
  python tests/test_svd.py --image scene.png --output my_video.mp4
  
  # Test motion variations
  python tests/test_svd.py --test-variations
        """
    )
    
    parser.add_argument(
        '--image',
        type=Path,
        help='Input image path (downloads test image if not provided)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path("test_output.mp4"),
        help='Output video path (default: test_output.mp4)'
    )
    
    parser.add_argument(
        '--test-variations',
        action='store_true',
        help='Test different motion settings'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎬" * 35)
    print(" " * 20 + "SVD VIDEO TEST")
    print(" " * 10 + "Stable Video Diffusion Pipeline")
    print("🎬" * 35 + "\n")
    
    try:
        # Get input image
        if args.image is None:
            # Download test image
            test_image_path = Path("test_image.png")
            if not test_image_path.exists():
                download_test_image(DEFAULT_TEST_IMAGE_URL, test_image_path)
            args.image = test_image_path
        
        # Run tests
        if args.test_variations:
            test_motion_variations(args.image, Path("test_variations"))
        else:
            test_basic_generation(args.image, args.output)
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        
        sys.exit(0)
        
    except VideoGenerationError as e:
        logger.error(f"\n❌ Video generation failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Test cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
