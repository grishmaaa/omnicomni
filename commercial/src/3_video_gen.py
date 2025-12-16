"""
Video Generation Module (3_video_gen.py)

Converts static images into cinematic video clips using Fal.ai Minimax.
Handles asynchronous processing with robust error handling and logging.

Author: Senior Python Developer (Async Media Processing)
Purpose: Motion Engine of AI Video Generator pipeline
"""

import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
import fal_client

# Import our existing Fal.ai client for cost tracking
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from commercial.clients.fal_client import FalClient

# ============================================================================
# Configuration & Constants
# ============================================================================

# Fal.ai model for image-to-video
MODEL_ID = "fal-ai/minimax-video/image-to-video"

# Default motion prompt (used if scene doesn't have specific guidance)
DEFAULT_MOTION_PROMPT = "High quality, cinematic motion, smooth camera movement"

# Video settings
VIDEO_DURATION = 5.0  # seconds per clip


def generate_videos(script_path: str = "script.json") -> list:
    """
    Generate cinematic video clips from static images.
    
    This function takes images from assets/images/ and converts them into
    5-second video clips using Fal.ai's Minimax image-to-video model.
    
    Process Flow:
    1. Upload local image to Fal.ai temporary storage
    2. Subscribe to video generation job (blocks until complete)
    3. Download generated video
    4. Save to assets/videos/
    
    Features:
    - Asynchronous processing with subscribe pattern
    - Idempotency: Skips already-generated videos
    - Error resilience: One failed video won't crash the batch
    - Progress tracking: Detailed logging for each scene
    
    Args:
        script_path: Path to screenplay JSON (default: "script.json")
        
    Returns:
        list: Paths to generated video files
        
    Technical Details:
        - Model: fal-ai/minimax-video/image-to-video
        - Duration: 5 seconds per clip
        - Upload: Uses fal_client.upload_file() for temporary storage
        - Processing: Uses subscribe() pattern (blocks until complete)
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
    
    # Set FAL_KEY for fal_client library
    os.environ["FAL_KEY"] = api_key
    
    # Set API key for fal_client
    fal_client.api_key = api_key
    
    # Load screenplay for context
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
    
    # Ensure directories exist
    images_dir = Path(__file__).parent.parent / "assets" / "images"
    videos_dir = Path(__file__).parent.parent / "assets" / "videos"
    
    if not images_dir.exists():
        raise FileNotFoundError(
            f"Images directory not found: {images_dir}\n"
            f"Run 2_image_gen.py first to generate images."
        )
    
    videos_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize cost tracking
    print(f"🔌 Connecting to Fal.ai...")
    print(f"   Model: {MODEL_ID}")
    print(f"   Duration: {VIDEO_DURATION}s per clip")
    print()
    
    generated_videos = []
    total_scenes = len(scenes)
    total_cost = 0.0
    
    # Process each scene
    for i, scene in enumerate(scenes, 1):
        scene_number = scene.get('scene_number', i)
        
        # Input image path
        image_filename = f"scene_{scene_number}.png"
        image_path = images_dir / image_filename
        
        # Output video path
        video_filename = f"scene_{scene_number}.mp4"
        video_path = videos_dir / video_filename
        
        # Idempotency check: Skip if already exists
        if video_path.exists():
            print(f"⏭️  Scene {scene_number}/{total_scenes}: Skipping (video already exists)")
            print(f"   File: {video_path}")
            generated_videos.append(video_path)
            continue
        
        # Check if input image exists
        if not image_path.exists():
            print(f"⚠️  Scene {scene_number}/{total_scenes}: Image not found, skipping")
            print(f"   Missing: {image_path}")
            continue
        
        print(f"🎬 Scene {scene_number}/{total_scenes}: Generating video...")
        print(f"   Input: {image_filename}")
        
        try:
            # Step 1: Upload image to Fal.ai temporary storage
            print(f"   📤 Uploading image to Fal.ai...")
            image_url = fal_client.upload_file(str(image_path))
            print(f"   ✅ Uploaded: {image_url[:50]}...")
            
            # Get motion prompt from scene or use default
            motion_prompt = scene.get('narration', DEFAULT_MOTION_PROMPT)
            
            # Step 2: Subscribe to video generation (blocks until complete)
            print(f"   🎥 Generating video (this may take 30-60 seconds)...")
            
            result = fal_client.subscribe(
                MODEL_ID,
                arguments={
                    "image_url": image_url,
                    "prompt": motion_prompt
                }
            )
            
            # Step 3: Extract video URL from result
            video_data = result.get("video", {})
            video_url = video_data.get("url")
            
            if not video_url:
                raise ValueError("No video URL in API response")
            
            print(f"   ✅ Video generated: {video_url[:50]}...")
            
            # Step 4: Download video
            print(f"   📥 Downloading video...")
            
            response = requests.get(video_url, stream=True, timeout=120)
            response.raise_for_status()
            
            # Save to disk
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"   ✅ Saved to: {video_path}")
            generated_videos.append(video_path)
            
            # Track cost (~$0.10 per 5s video)
            total_cost += 0.10
            
        except requests.RequestException as e:
            print(f"   ❌ Download failed: {e}")
            print(f"   Continuing with next scene...")
            
        except ValueError as e:
            print(f"   ❌ API error: {e}")
            print(f"   Continuing with next scene...")
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            print(f"   This could be due to:")
            print(f"      - Content safety filter")
            print(f"      - API rate limit")
            print(f"      - Network timeout")
            print(f"   Continuing with next scene...")
        
        print()
    
    # Summary
    print("=" * 70)
    print(f"✅ Video generation complete!")
    print(f"   Generated: {len(generated_videos)}/{total_scenes} videos")
    print(f"   Output directory: {videos_dir}")
    print(f"   Estimated cost: ${total_cost:.2f}")
    print("=" * 70)
    
    return generated_videos


# ============================================================================
# Implementation Note: subscribe() vs submit()
# ============================================================================
"""
WHY WE USE fal_client.subscribe() INSTEAD OF fal_client.submit():

1. SUBSCRIBE (Blocking, Recommended)
   - Blocks execution until job completes
   - Handles WebSocket connections automatically
   - Built-in polling and status checking
   - Returns result directly when ready
   - Simpler error handling
   - Code example:
     result = fal_client.subscribe("model-id", arguments={...})
     # Result is available immediately after this line

2. SUBMIT (Fire-and-Forget, Advanced)
   - Returns immediately with a job ID
   - Requires manual polling in a loop
   - Must implement your own status checking
   - More complex error handling
   - Useful for batch processing or background jobs
   - Code example:
     job = fal_client.submit("model-id", arguments={...})
     while True:
         status = fal_client.status(job.request_id)
         if status.completed:
             result = fal_client.result(job.request_id)
             break
         time.sleep(5)  # Manual polling

FOR THIS USE CASE:
- We use subscribe() because:
  * We want to process scenes sequentially
  * We need the result before moving to the next scene
  * We want automatic error handling
  * We don't need parallel processing (videos are slow anyway)
  
- We would use submit() if:
  * Processing multiple videos in parallel
  * Building a queue system
  * Need to return control to user immediately
  * Implementing a webhook-based workflow
"""


# ============================================================================
# Execution Block
# ============================================================================

if __name__ == "__main__":
    """
    Example usage: Generate videos from images.
    
    Prerequisites:
        1. Run 1_script_gen.py to create script.json
        2. Run 2_image_gen.py to create images
        3. Set FAL_API_KEY in .env.commercial
    
    To run this script:
        cd commercial/src
        python 3_video_gen.py
    
    Output:
        - Prints generation progress to console
        - Saves videos to commercial/assets/videos/
        - Shows cost estimate at the end
        
    Note:
        Video generation is SLOW (~30-60 seconds per clip)
        Be patient and watch the progress logs
    """
    
    print("=" * 70)
    print("🎬 AI Video Generator - Video Generation Module")
    print("=" * 70)
    print()
    
    try:
        # Generate videos
        video_paths = generate_videos()
        
        print()
        print("🎥 Generated Videos:")
        for path in video_paths:
            print(f"   - {path.name}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure to run previous steps first:")
        print("   1. python 1_script_gen.py")
        print("   2. python 2_image_gen.py")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Check your .env.commercial file for FAL_API_KEY")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
