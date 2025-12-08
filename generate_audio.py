#!/usr/bin/env python3
"""
Task 3: Audio Engine for Video Pipeline
Generates high-quality AI voiceovers from storyboard JSON using edge-tts

Requirements:
- Async/await implementation
- CLI with argparse
- Handles empty/null text
- Filename sanitization
- Rate limiting
- Progress feedback
- UTF-8 encoding
"""

import json
import asyncio
import os
import argparse
from pathlib import Path
import edge_tts
import sys


# ============================================================================
# CONFIGURATION
# ============================================================================

# Voice Selection - easily changeable
# Movie-trailer style: "en-US-ChristopherNeural"
# Clear female: "en-US-AriaNeural"
# British male: "en-GB-RyanNeural"
DEFAULT_VOICE = "en-US-ChristopherNeural"

# Output directory
DEFAULT_OUTPUT_DIR = "output/audio"

# Rate limiting delay (seconds)
RATE_LIMIT_DELAY = 0.5


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sanitize_filename(text: str) -> str:
    """
    Create safe filename from text
    Removes special characters and limits length
    """
    # Remove non-alphanumeric characters except spaces and hyphens
    safe = "".join(c for c in text if c.isalnum() or c in (" ", "-", "_"))
    # Replace spaces with underscores
    safe = safe.replace(" ", "_")
    # Lowercase and limit length
    safe = safe[:50].strip("_").lower()
    return safe or "untitled"


def load_json(filepath: str) -> list:
    """
    Load and validate JSON file
    Handles UTF-8 encoding properly
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of scenes")
        
        return data
    
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        sys.exit(1)


def create_output_directory(json_path: str, output_base: str) -> Path:
    """
    Create output directory based on JSON filename
    Overwrites existing files for quick iteration
    """
    # Get base name from JSON file
    json_file = Path(json_path)
    base_name = json_file.stem  # filename without extension
    
    # Create output path
    output_dir = Path(output_base) / base_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


# ============================================================================
# ASYNC AUDIO GENERATION
# ============================================================================

async def generate_scene_audio(
    scene: dict,
    output_dir: Path,
    voice: str,
    scene_num: int,
    total_scenes: int
) -> bool:
    """
    Generate audio for a single scene
    
    Returns:
        True if successful, False if skipped
    """
    # Extract text (try multiple field names for compatibility)
    text = scene.get("audio_text") or scene.get("narration_text") or scene.get("text", "")
    
    # Get scene ID
    scene_id = scene.get("scene_id", scene_num)
    
    # Check for empty text
    if not text or text.strip() == "":
        print(f"⚠️  Skipping Scene {scene_id} (No text)")
        return False
    
    # Create safe filename
    filename = f"scene_{scene_id:02d}_audio.mp3"
    output_path = output_dir / filename
    
    # Progress feedback
    print(f"🎤 Generating Scene {scene_num}/{total_scenes} ({scene_id})...")
    
    try:
        # Create TTS instance
        communicate = edge_tts.Communicate(text, voice)
        
        # Generate and save audio
        await communicate.save(str(output_path))
        
        print(f"   ✅ Saved: {filename}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error generating audio: {e}")
        return False


async def generate_all_audio(
    scenes: list,
    output_dir: Path,
    voice: str
) -> dict:
    """
    Generate audio for all scenes with rate limiting
    
    Returns:
        Summary statistics
    """
    total_scenes = len(scenes)
    successful = 0
    skipped = 0
    failed = 0
    
    print(f"\n🎬 Processing {total_scenes} scenes...")
    print(f"🗣️  Voice: {voice}")
    print(f"📁 Output: {output_dir}\n")
    
    for i, scene in enumerate(scenes, 1):
        result = await generate_scene_audio(
            scene,
            output_dir,
            voice,
            i,
            total_scenes
        )
        
        if result:
            successful += 1
        else:
            skipped += 1
        
        # Rate limiting (except for last scene)
        if i < total_scenes:
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    return {
        "total": total_scenes,
        "successful": successful,
        "skipped": skipped,
        "failed": failed
    }


# ============================================================================
# MAIN ASYNC FUNCTION
# ============================================================================

async def main():
    """Main async execution"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate AI voiceovers from video storyboard JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_audio.py --input project_folder/1_scripts/my_story_scenes.json
  python generate_audio.py --input scenes.json --voice en-US-AriaNeural
  python generate_audio.py --input scenes.json --output my_audio --voice en-GB-RyanNeural

List available voices:
  edge-tts --list-voices
  edge-tts --list-voices | grep -i "Name: en-"
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to JSON storyboard file'
    )
    
    parser.add_argument(
        '--output',
        default=DEFAULT_OUTPUT_DIR,
        help=f'Output directory base (default: {DEFAULT_OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--voice',
        default=DEFAULT_VOICE,
        help=f'Edge TTS voice name (default: {DEFAULT_VOICE})'
    )
    
    args = parser.parse_args()
    
    # Header
    print("\n" + "🎙️ " * 35)
    print(" " * 20 + "AUDIO ENGINE")
    print(" " * 15 + "Video Scene Narration")
    print("🎙️ " * 35 + "\n")
    
    # Load JSON
    print(f"📄 Loading: {args.input}")
    scenes = load_json(args.input)
    print(f"✅ Loaded {len(scenes)} scenes\n")
    
    # Create output directory
    output_dir = create_output_directory(args.input, args.output)
    
    # Generate audio
    stats = await generate_all_audio(scenes, output_dir, args.voice)
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📊 Statistics:")
    print(f"   Total scenes: {stats['total']}")
    print(f"   ✅ Successful: {stats['successful']}")
    print(f"   ⚠️  Skipped:    {stats['skipped']}")
    print(f"   ❌ Failed:     {stats['failed']}")
    print(f"\n📁 Audio files saved to: {output_dir}")
    print("\n💡 To verify: Open the folder and play the MP3 files")
    print("=" * 70 + "\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        # Run async main
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
