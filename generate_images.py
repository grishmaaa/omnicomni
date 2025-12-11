#!/usr/bin/env python3
"""
Image Generation CLI - Task 6
Generates images from video scene JSON using Flux-Schnell

Follows OmniComni patterns from generate_audio.py
Reads from pipeline_manager.py output format
"""

import json
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict

from src.image.sd_client import SDImageGenerator as FluxImageGenerator


# ============================================================================
# CONFIGURATION
# ============================================================================

# Image generation settings
DEFAULT_NUM_VARIATIONS = 1  # Images per scene
DEFAULT_STEPS = 4  # Flux-Schnell optimized for 4 steps
DEFAULT_SIZE = 1024  # 1024x1024 default

# Output directory
DEFAULT_OUTPUT_BASE = "output/images"


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
    """
    Create safe directory name from topic
    Reuses logic from pipeline_manager.py
    """
    import re
    safe = re.sub(r'[^\w\s-]', '', text)
    safe = re.sub(r'[\s]+', '_', safe)
    return safe[:50].strip('_').lower()


def load_scenes(json_path: Path) -> List[Dict]:
    """
    Load and validate scenes JSON
    
    Args:
        json_path: Path to scenes.json file
        
    Returns:
        List of scene dictionaries
        
    Raises:
        FileNotFoundError: If JSON doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    if not json_path.exists():
        raise FileNotFoundError(f"Scenes file not found: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            scenes = json.load(f)
        
        if not isinstance(scenes, list):
            raise ValueError("JSON must be an array of scenes")
        
        logger.info(f"✅ Loaded {len(scenes)} scenes from {json_path}")
        return scenes
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        raise


def build_image_prompt(scene: Dict, global_style: str = "cinematic") -> str:
    """
    Build high-quality image prompt from scene data
    
    Uses Task 13 Advanced Prompt Engineering if structured fields available,
    falls back to legacy visual_prompt field
    
    Args:
        scene: Scene dictionary with visual fields
        global_style: Style preset (cinematic, anime, photorealistic, etc.)
        
    Returns:
        Enhanced prompt for Flux/SD
    """
    try:
        from src.image.prompt_builder import build_flux_prompt, QualityLevel
        
        # Use advanced prompt builder
        prompts = build_flux_prompt(
            scene=scene,
            global_style=global_style,
            quality=QualityLevel.HIGH
        )
        
        return prompts['positive']
        
    except ImportError:
        # Fallback: Legacy mode if prompt_builder not available
        visual_prompt = scene.get("visual_prompt", "")
        
        if not visual_prompt:
            logger.warning(f"Scene {scene.get('scene_id', '?')} has no visual_prompt")
            return "A cinematic scene, 4k, highly detailed"
        
        return visual_prompt


# ============================================================================
# MAIN GENERATION LOGIC
# ============================================================================

def generate_images_for_scenes(
    scenes: List[Dict],
    output_dir: Path,
    num_variations: int = DEFAULT_NUM_VARIATIONS,
    seed_base: int = 42
) -> Dict:
    """
    Generate images for all scenes
    
    Args:
        scenes: List of scene dictionaries
        output_dir: Directory to save images
        num_variations: Number of image variations per scene
        seed_base: Base seed for reproducibility
        
    Returns:
        Statistics dictionary
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Flux generator
    logger.info("🎨 Initializing Flux-Schnell generator...")
    generator = FluxImageGenerator()
    
    # Track statistics
    total_scenes = len(scenes)
    successful = 0
    failed = 0
    total_images = 0
    
    logger.info(f"\n🖼️  Generating {num_variations} variation(s) per scene")
    logger.info(f"📁 Output: {output_dir}\n")
    
    # Process each scene
    for i, scene in enumerate(scenes, 1):
        scene_id = scene.get("scene_id", i)
        
        logger.info(f"{'='*70}")
        logger.info(f"Scene {i}/{total_scenes} (ID: {scene_id})")
        logger.info(f"{'='*70}")
        
        # Build prompt
        prompt = build_image_prompt(scene)
        logger.info(f"Prompt: {prompt[:100]}...")
        
        # Generate variations
        scene_success = True
        for var_idx in range(1, num_variations + 1):
            try:
                # Create filename
                filename = f"scene_{scene_id:02d}_var_{var_idx:02d}.png"
                output_path = output_dir / filename
                
                # Calculate seed (reproducible but different per variation)
                seed = seed_base + (scene_id * 1000) + var_idx
                
                logger.info(f"  Generating variation {var_idx}/{num_variations}...")
                
                # Generate image
                generator.generate(
                    prompt=prompt,
                    output_path=output_path,
                    seed=seed,
                    num_inference_steps=DEFAULT_STEPS
                )
                
                total_images += 1
                
            except Exception as e:
                logger.error(f"  ❌ Failed variation {var_idx}: {e}")
                scene_success = False
        
        if scene_success:
            successful += 1
        else:
            failed += 1
        
        logger.info("")  # Blank line between scenes
    
    # Summary
    stats = {
        "total_scenes": total_scenes,
        "successful_scenes": successful,
        "failed_scenes": failed,
        "total_images_generated": total_images,
        "output_directory": str(output_dir)
    }
    
    return stats


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate images from video scene JSON using Flux-Schnell",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From pipeline output
  python generate_images.py --input output/20241208_073941_topic_3/1_scripts/topic_3_scenes.json
  
  # Custom variations
  python generate_images.py --input scenes.json --variations 3
  
  # Custom output location
  python generate_images.py --input scenes.json --output my_images
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to scenes JSON file'
    )
    
    parser.add_argument(
        '--output',
        default=DEFAULT_OUTPUT_BASE,
        help=f'Output directory base (default: {DEFAULT_OUTPUT_BASE})'
    )
    
    parser.add_argument(
        '--variations',
        type=int,
        default=DEFAULT_NUM_VARIATIONS,
        help=f'Number of image variations per scene (default: {DEFAULT_NUM_VARIATIONS})'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Base random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎨" * 35)
    print(" " * 20 + "IMAGE GENERATOR")
    print(" " * 15 + "Flux-Schnell Pipeline")
    print("🎨" * 35 + "\n")
    
    try:
        # Load scenes
        input_path = Path(args.input)
        scenes = load_scenes(input_path)
        
        # Determine output directory
        # Use input filename as slug
        topic_slug = input_path.stem.replace("_scenes", "")
        output_dir = Path(args.output) / topic_slug
        
        # Generate images
        stats = generate_images_for_scenes(
            scenes=scenes,
            output_dir=output_dir,
            num_variations=args.variations,
            seed_base=args.seed
        )
        
        # Final summary
        print("\n" + "="*70)
        print("GENERATION COMPLETE")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   Total scenes: {stats['total_scenes']}")
        print(f"   ✅ Successful: {stats['successful_scenes']}")
        print(f"   ❌ Failed:     {stats['failed_scenes']}")
        print(f"   🖼️  Total images: {stats['total_images_generated']}")
        print(f"\n📁 Images saved to: {stats['output_directory']}")
        print("="*70 + "\n")
        
        # Success if at least some images generated
        if stats['total_images_generated'] > 0:
            print("✅ SUCCESS: Image generation complete!")
            sys.exit(0)
        else:
            print("❌ FAILED: No images generated")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
