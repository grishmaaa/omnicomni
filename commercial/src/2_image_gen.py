"""
Image Generation Module (2_image_gen.py)

Generates cinematic 16:9 images from screenplay using Fal.ai FLUX.
Ensures visual consistency across all scenes with global style injection.

Author: Generative Media Engineer
Purpose: Asset production module of AI Video Generator pipeline
"""

import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Import our existing Fal.ai client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from commercial.clients.fal_client import FalClient

# ============================================================================
# Configuration & Constants
# ============================================================================

# Global style for visual consistency across all scenes
GLOBAL_STYLE = (
    "Cinematic lighting, hyper-realistic, 8k, film grain, "
    "shot on 35mm lens, professional color grading, depth of field"
)

# Aspect ratio configuration (16:9 landscape for cinematic video)
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# Fal.ai model selection
# Options:
#   - "fal-ai/flux/dev" (default): Balanced quality/speed, $0.025/image
#   - "fal-ai/flux-pro" (v1.1): Highest detail, $0.055/image
MODEL_ID = "fal-ai/flux/dev"

# Quality settings
INFERENCE_STEPS = 28  # Higher = better quality, slower (range: 20-50)
GUIDANCE_SCALE = 3.5  # Higher = more prompt adherence (range: 1.0-7.0)


def generate_images(script_path: str = "script.json") -> list:
    """
    Generate cinematic images from screenplay.
    
    This function reads the screenplay JSON, generates 16:9 landscape images
    for each scene using Fal.ai FLUX, and saves them to assets/images/.
    
    Features:
    - Idempotency: Skips already-generated images to save costs
    - Style consistency: Appends GLOBAL_STYLE to every prompt
    - Error resilience: One failed image won't crash the batch
    - Progress tracking: Prints status for each scene
    
    Args:
        script_path: Path to screenplay JSON (default: "script.json")
        
    Returns:
        list: Paths to generated image files
        
    Technical Details:
        - Aspect Ratio: 16:9 (1920x1080) for cinematic video
        - Model: fal-ai/flux/dev (high prompt adherence)
        - Style: Global style constant appended to all prompts
        - Idempotency: Checks for existing files before API call
    """
    
    # Load environment variables from .env.commercial
    env_path = Path(__file__).parent.parent.parent / ".env.commercial"
    load_dotenv(env_path)
    
    # Get API key from environment
    api_key = os.getenv("FAL_API_KEY")
    if not api_key:
        raise ValueError(
            "FAL_API_KEY not found in environment. "
            "Please set it in your .env file."
        )
    
    # Set FAL_KEY for fal_client library (it expects this env var)
    os.environ["FAL_KEY"] = api_key
    
    # Load screenplay
    script_file = Path(__file__).parent.parent / script_path
    if not script_file.exists():
        raise FileNotFoundError(
            f"Screenplay not found: {script_file}\n"
            f"Run 1_script_gen.py first to generate the screenplay."
        )
    
    with open(script_file, 'r', encoding='utf-8') as f:
        screenplay = json.load(f)
    
    scenes = screenplay.get('scenes', [])
    if not scenes:
        raise ValueError("No scenes found in screenplay")
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent.parent / "assets" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize Fal.ai client
    print(f"🔌 Connecting to Fal.ai...")
    print(f"   Model: {MODEL_ID}")
    print(f"   Resolution: {IMAGE_WIDTH}x{IMAGE_HEIGHT} (16:9 cinematic)")
    print(f"   Global Style: {GLOBAL_STYLE[:50]}...")
    print()
    
    client = FalClient(api_key=api_key)
    
    # Ensure output directory exists
    output_dir = Path(__file__).parent.parent / "assets" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_images = []
    total_scenes = len(scenes)
    
    # Process each scene
    for i, scene in enumerate(scenes, 1):
        scene_number = scene.get('scene_number', i)
        image_prompt = scene.get('image_prompt', '')
        
        # Output filename
        output_filename = f"scene_{scene_number}.png"
        output_path = output_dir / output_filename
        
        # Idempotency check: Skip if already exists
        if output_path.exists():
            print(f"⏭️  Scene {scene_number}/{total_scenes}: Skipping (already exists)")
            print(f"   File: {output_path}")
            generated_images.append(output_path)
            continue
        
        # Construct combined prompt with global style
        combined_prompt = f"{image_prompt}, {GLOBAL_STYLE}"
        
        print(f"🎨 Scene {scene_number}/{total_scenes}: Generating...")
        print(f"   Prompt: {image_prompt[:80]}...")
        
        try:
            # Call Fal.ai API
            image_result = client.generate_image(
                prompt=combined_prompt,
                width=IMAGE_WIDTH,
                height=IMAGE_HEIGHT,
                num_inference_steps=INFERENCE_STEPS,
                guidance_scale=GUIDANCE_SCALE
            )
            
            # Download image
            print(f"   Downloading from: {image_result.url[:50]}...")
            
            response = requests.get(image_result.url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Save to disk
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   ✅ Saved to: {output_path}")
            generated_images.append(output_path)
            
        except requests.RequestException as e:
            print(f"   ❌ Download failed: {e}")
            print(f"   Continuing with next scene...")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            print(f"   Continuing with next scene...")
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"✅ Image generation complete!")
    print(f"   Generated: {len(generated_images)}/{total_scenes} images")
    print(f"   Output directory: {output_dir}")
    print(f"   Total cost: ${client.get_cost_estimate():.2f}")
    print("=" * 70)
    
    return generated_images


# ============================================================================
# Technical Note: Model Selection
# ============================================================================
"""
MODEL COMPARISON:

1. fal-ai/flux/dev (Current Default)
   - Quality: High (excellent prompt adherence, good texture detail)
   - Speed: ~8-12 seconds per image
   - Cost: ~$0.025 per image
   - Best for: Production workflows, balanced quality/cost

2. fal-ai/flux-pro (v1.1)
   - Quality: Highest (superior detail, better lighting, more realistic)
   - Speed: ~15-20 seconds per image
   - Cost: ~$0.055 per image (2.2x more expensive)
   - Best for: Premium content, client work, final deliverables

HOW TO SWITCH:
Change line 37:
    MODEL_ID = "fal-ai/flux-pro"

TRADE-OFF ANALYSIS:
- For 5-scene video:
  - flux/dev: $0.125 total (~12 seconds each)
  - flux-pro: $0.275 total (~20 seconds each)
  
- Recommendation:
  - Use flux/dev for testing and iteration
  - Use flux-pro for final production renders
  - Consider flux-pro if client is paying premium rates

QUALITY DIFFERENCE:
- flux/dev: 90% quality, great for most use cases
- flux-pro: 100% quality, noticeable improvement in:
  * Skin textures and fabric detail
  * Lighting realism and shadows
  * Color accuracy and depth
  * Fine details (hair, eyes, reflections)
"""


# ============================================================================
# Execution Block
# ============================================================================

if __name__ == "__main__":
    """
    Example usage: Generate images from screenplay.
    
    Prerequisites:
        1. Run 1_script_gen.py first to create script.json
        2. Set FAL_API_KEY in .env.commercial
    
    To run this script:
        cd commercial/src
        python 2_image_gen.py
    
    Output:
        - Prints generation progress to console
        - Saves images to commercial/assets/images/
        - Shows cost estimate at the end
    """
    
    print("=" * 70)
    print("🎨 AI Video Generator - Image Generation Module")
    print("=" * 70)
    print()
    
    try:
        # Generate images
        image_paths = generate_images()
        
        print()
        print("📸 Generated Images:")
        for path in image_paths:
            print(f"   - {path.name}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure to run 1_script_gen.py first!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Check your .env.commercial file for FAL_API_KEY")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
