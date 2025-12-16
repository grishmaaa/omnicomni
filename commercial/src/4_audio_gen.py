"""
Audio Generation Module (4_audio_gen.py)

Generates professional voiceover narration using ElevenLabs TTS.
Implements cost-efficient caching and character usage tracking.

Author: Voice-Tech Integration Engineer
Purpose: Audio synthesis module of AI Video Generator pipeline
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Import our existing ElevenLabs client for reference
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ============================================================================
# Configuration & Constants
# ============================================================================

# Voice ID Configuration
# To find more voices:
# 1. Go to https://elevenlabs.io/app/voice-library
# 2. Click on a voice you like
# 3. Copy the Voice ID from the URL or voice settings
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George - Deep, authoritative male voice

# Alternative popular voices:
# "21m00Tcm4TlvDq8ikWAM"  # Rachel - Calm, professional female
# "pNInz6obpgDQGcFmaJgB"  # Adam - Deep, authoritative male
# "EXAVITQu4vr4xnSDxMaL"  # Bella - Soft, friendly female
# "ErXwobaYiN019PkySvjV"  # Antoni - Well-rounded male

# Model configuration
MODEL_ID = "eleven_multilingual_v2"  # High-fidelity, supports multiple languages

# Voice settings for optimal quality
VOICE_SETTINGS = {
    "stability": 0.5,           # 0-1: Higher = more consistent, lower = more expressive
    "similarity_boost": 0.75,   # 0-1: Higher = closer to original voice
    "style": 0.0,               # 0-1: Higher = more stylistic exaggeration
    "use_speaker_boost": True   # Enhances clarity and presence
}


def generate_audio(script_path: str = "script.json") -> list:
    """
    Generate professional voiceover narration from screenplay.
    
    This function reads the screenplay JSON and generates high-fidelity
    audio narration for each scene using ElevenLabs TTS.
    
    Features:
    - Idempotency: Skips already-generated audio to save costs
    - Character tracking: Logs character count for cost awareness
    - Modern SDK: Uses client.text_to_speech.convert() pattern
    - Error resilience: One failed audio won't crash the batch
    
    Args:
        script_path: Path to screenplay JSON (default: "script.json")
        
    Returns:
        list: Paths to generated audio files
        
    Technical Details:
        - Service: ElevenLabs
        - Model: eleven_multilingual_v2 (high-fidelity)
        - Voice: Configurable via VOICE_ID constant
        - Format: MP3 (optimized for web/video)
        - Cost: ~$0.30 per 1,000 characters
    """
    
    # Load environment variables from .env.commercial
    env_path = Path(__file__).parent.parent.parent / ".env.commercial"
    load_dotenv(env_path)
    
    # Get API key from environment
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY not found in environment. "
            "Please set it in your .env file."
        )
    
    # Initialize ElevenLabs client (modern SDK pattern)
    print(f"🔌 Connecting to ElevenLabs...")
    print(f"   Model: {MODEL_ID}")
    print(f"   Voice ID: {VOICE_ID}")
    print()
    
    client = ElevenLabs(api_key=api_key)
    
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
    audio_dir = Path(__file__).parent.parent / "assets" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    generated_audio = []
    total_scenes = len(scenes)
    total_characters = 0
    
    # Process each scene
    for i, scene in enumerate(scenes, 1):
        scene_number = scene.get('scene_number', i)
        narration = scene.get('narration', '')
        
        if not narration:
            print(f"⚠️  Scene {scene_number}/{total_scenes}: No narration text, skipping")
            continue
        
        # Output filename
        output_filename = f"scene_{scene_number}.mp3"
        output_path = audio_dir / output_filename
        
        # Idempotency check: Skip if already exists
        if output_path.exists():
            print(f"⏭️  Scene {scene_number}/{total_scenes}: Audio exists, skipping")
            print(f"   File: {output_path}")
            generated_audio.append(output_path)
            continue
        
        # Character count for cost awareness
        char_count = len(narration)
        total_characters += char_count
        
        print(f"🎙️  Scene {scene_number}/{total_scenes}: Generating audio...")
        print(f"   Text: {narration[:60]}...")
        print(f"   Characters: {char_count}")
        
        try:
            # Configure voice settings
            voice_settings = VoiceSettings(
                stability=VOICE_SETTINGS["stability"],
                similarity_boost=VOICE_SETTINGS["similarity_boost"],
                style=VOICE_SETTINGS["style"],
                use_speaker_boost=VOICE_SETTINGS["use_speaker_boost"]
            )
            
            # Call ElevenLabs API (modern SDK pattern)
            audio_generator = client.text_to_speech.convert(
                text=narration,
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                voice_settings=voice_settings
            )
            
            # Aggregate audio bytes from generator
            print(f"   📥 Receiving audio stream...")
            audio_bytes = b""
            for chunk in audio_generator:
                audio_bytes += chunk
            
            # Save to file in binary mode
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            print(f"   ✅ Saved to: {output_path}")
            print(f"   Size: {len(audio_bytes) / 1024:.1f} KB")
            generated_audio.append(output_path)
            
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            print(f"   This could be due to:")
            print(f"      - Invalid API key")
            print(f"      - Insufficient credits")
            print(f"      - Rate limit exceeded")
            print(f"   Continuing with next scene...")
        
        print()
    
    # Cost estimate
    cost_per_thousand = 0.30
    estimated_cost = (total_characters / 1000) * cost_per_thousand
    
    # Summary
    print("=" * 70)
    print(f"✅ Audio generation complete!")
    print(f"   Generated: {len(generated_audio)}/{total_scenes} audio files")
    print(f"   Total characters: {total_characters:,}")
    print(f"   Estimated cost: ${estimated_cost:.2f}")
    print(f"   Output directory: {audio_dir}")
    print("=" * 70)
    
    return generated_audio


# ============================================================================
# Voice ID Guide
# ============================================================================
"""
HOW TO FIND AND CHANGE VOICE ID:

1. Go to ElevenLabs Voice Library:
   https://elevenlabs.io/app/voice-library

2. Browse available voices:
   - Filter by gender, accent, age, use case
   - Click "Preview" to hear samples
   - Choose a voice that matches your content style

3. Get the Voice ID:
   Method A: From URL
   - Click on a voice
   - Look at the URL: https://elevenlabs.io/app/voice-lab/voice/[VOICE_ID]
   - Copy the ID after "voice/"
   
   Method B: From Voice Settings
   - Click on a voice
   - Go to "Settings" tab
   - Copy the "Voice ID" field

4. Update this file:
   Change line 24:
   VOICE_ID = "your_new_voice_id_here"

POPULAR VOICE RECOMMENDATIONS:

For Corporate/Professional:
- Rachel (21m00Tcm4TlvDq8ikWAM): Calm, clear female
- Adam (pNInz6obpgDQGcFmaJgB): Authoritative male

For Storytelling/Narration:
- George (JBFqnCBsd6RMkjVDRZzb): Deep, engaging male
- Bella (EXAVITQu4vr4xnSDxMaL): Warm, friendly female

For TikTok/Social Media:
- Josh (TxGEqnHWrfWFTfGW9XjX): Young, energetic male
- Elli (MF3mGyEYCl7XYWbV9V6O): Expressive, emotional female
"""


# ============================================================================
# Execution Block
# ============================================================================

if __name__ == "__main__":
    """
    Example usage: Generate audio narration from screenplay.
    
    Prerequisites:
        1. Run 1_script_gen.py to create script.json
        2. Set ELEVENLABS_API_KEY in .env.commercial
    
    To run this script:
        cd commercial/src
        python 4_audio_gen.py
    
    Output:
        - Prints generation progress to console
        - Saves audio to commercial/assets/audio/
        - Shows character count and cost estimate
        
    Note:
        ElevenLabs charges by character (~$0.30 per 1,000 chars)
        The idempotency check prevents accidental re-generation
    """
    
    print("=" * 70)
    print("🎙️  AI Video Generator - Audio Generation Module")
    print("=" * 70)
    print()
    
    try:
        # Generate audio
        audio_paths = generate_audio()
        
        print()
        print("🔊 Generated Audio Files:")
        for path in audio_paths:
            print(f"   - {path.name}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure to run 1_script_gen.py first!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Check your .env.commercial file for ELEVENLABS_API_KEY")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
