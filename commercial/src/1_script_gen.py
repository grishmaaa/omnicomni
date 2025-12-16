"""
Script Generation Module (1_script_gen.py)

Converts a user topic into a structured JSON screenplay using Groq's Llama-3.3-70B.
This module wraps the existing GroqClient for compatibility with the requested API.

Author: Senior Backend Engineer
Purpose: First module of AI Video Generator pipeline
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Import OpenAI client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from commercial.clients.openai_client import OpenAIClient, StoryResponse


def generate_script(topic: str, num_scenes: int = 5, style: str = "cinematic") -> dict:
    """
    Generate a structured screenplay from a topic.
    
    This function connects to Groq API using Llama-3.3-70B and converts
    the user input into a strictly validated JSON screenplay.
    
    Args:
        topic: The video topic/theme (e.g., "The History of Espresso")
        num_scenes: Number of scenes to generate (default: 5)
        style: Visual style - "cinematic", "anime", or "photorealistic"
        
    Returns:
        dict: Structured screenplay with scenes
        
    Technical Details:
        - Uses response_format={"type": "json_object"} for strict JSON compliance
        - Validates output with Pydantic schemas
        - Optimized prompts for Flux/Midjourney image generation
        - Engaging narration style for TikTok/Reels
        
    Example Output Schema:
        {
          "title": "The History of Espresso",
          "style": "cinematic",
          "scenes": [
            {
              "scene_id": 1,
              "visual_subject": "Vintage Italian espresso machine",
              "visual_action": "Steam rising from freshly pulled shot",
              "background_environment": "1950s Italian café, warm lighting",
              "lighting": "Soft golden hour, rim lighting on chrome",
              "camera_shot": "Medium close-up, 35mm lens, shallow depth of field",
              "narration": "In 1884, Angelo Moriondo changed coffee forever...",
              "duration": 5.0
            }
          ]
        }
    """
    
    # Load environment variables from .env.commercial
    env_path = Path(__file__).parent.parent.parent / ".env.commercial"
    load_dotenv(env_path)
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment. "
            "Please set it in your .env file."
        )
    
    # Initialize OpenAI client
    print(f"🔌 Connecting to OpenAI API...")
    client = OpenAIClient(api_key=api_key, model="gpt-4o-mini")
    
    # Generate story using our robust client
    print(f"🎬 Generating {num_scenes}-scene screenplay for: '{topic}'")
    print(f"   Style: {style}")
    print(f"   Model: Llama-3.3-70B")
    
    try:
        # Call the existing GroqClient (which already uses response_format=json_object)
        story: StoryResponse = client.generate_story(
            topic=topic,
            num_scenes=num_scenes,
            style=style
        )
        
        # Convert Pydantic model to dict for JSON serialization
        screenplay = {
            "title": story.title,
            "style": story.style,
            "scenes": [
                {
                    "scene_number": scene.scene_id,
                    "image_prompt": _build_flux_optimized_prompt(scene),
                    "narration": scene.narration,
                    "estimated_duration": int(scene.duration)
                }
                for scene in story.scenes
            ]
        }
        
        # Save to script.json in project root
        output_path = Path(__file__).parent.parent / "script.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(screenplay, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Screenplay saved to: {output_path}")
        print(f"   Title: {story.title}")
        print(f"   Scenes: {len(story.scenes)}")
        print(f"   Cost: ${client.get_cost_estimate():.4f}")
        
        return screenplay
        
    except Exception as e:
        print(f"❌ Error generating screenplay: {e}")
        raise


def _build_flux_optimized_prompt(scene) -> str:
    """
    Build Flux/Midjourney-optimized image prompt from scene data.
    
    This converts structured scene data into a single, keyword-rich prompt
    optimized for diffusion models like Flux and Midjourney.
    
    Format: "subject doing action, environment, lighting, camera, quality tags"
    
    Example:
        Input: scene with subject="cat", action="sitting", environment="garden"
        Output: "fluffy cat sitting peacefully, lush garden background, soft natural lighting, medium shot, 8k, detailed fur texture, depth of field"
    """
    components = []
    
    # Subject + Action (most important)
    if hasattr(scene, 'visual_subject') and hasattr(scene, 'visual_action'):
        components.append(f"{scene.visual_subject} {scene.visual_action}")
    
    # Environment
    if hasattr(scene, 'background_environment'):
        components.append(scene.background_environment)
    
    # Lighting
    if hasattr(scene, 'lighting'):
        components.append(scene.lighting)
    
    # Camera shot
    if hasattr(scene, 'camera_shot'):
        components.append(scene.camera_shot)
    
    # Quality tags (Flux/Midjourney optimization)
    quality_tags = "8k, highly detailed, professional photography, cinematic composition"
    components.append(quality_tags)
    
    # Join with commas (diffusion model standard)
    return ", ".join(components)


# ============================================================================
# Execution Block
# ============================================================================

if __name__ == "__main__":
    """
    Example usage: Generate a screenplay about espresso history.
    
    To run this script:
        cd commercial/src
        python 1_script_gen.py
    
    Output:
        - Prints generation progress to console
        - Saves screenplay to commercial/script.json
    """
    
    # Sample topic (change this to generate different content)
    SAMPLE_TOPIC = "The Art of Luxury Timepieces"
    
    print("=" * 70)
    print("🎬 AI Video Generator - Script Generation Module")
    print("=" * 70)
    print()
    
    # Generate the screenplay
    screenplay = generate_script(
        topic=SAMPLE_TOPIC,
        num_scenes=5,
        style="cinematic"
    )
    
    print()
    print("=" * 70)
    print("📄 Generated Screenplay Preview:")
    print("=" * 70)
    print(f"\nTitle: {screenplay['title']}")
    print(f"Style: {screenplay['style']}")
    print(f"\nScenes:")
    
    for scene in screenplay['scenes']:
        print(f"\n  Scene {scene['scene_number']}:")
        print(f"    Image: {scene['image_prompt'][:80]}...")
        print(f"    Narration: {scene['narration']}")
        print(f"    Duration: {scene['estimated_duration']}s")
    
    print()
    print("=" * 70)
    print("✅ Script generation complete!")
    print("=" * 70)
