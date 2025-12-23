"""
ElevenLabs API Client for Voice Synthesis

Professional text-to-speech with emotion control and voice cloning.
"""

import logging
from pathlib import Path
from typing import Optional, List
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings

logger = logging.getLogger(__name__)


class ElevenLabsClient:
    """
    ElevenLabs API client for voice synthesis
    
    Features:
    - Professional neural voices
    - Emotion and stability control
    - Character usage tracking for cost monitoring
    """
    
    # Popular voice presets
    VOICE_PRESETS = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",  # Calm, professional female
        "adam": "pNInz6obpgDQGcFmaJgB",    # Deep, authoritative male
        "bella": "EXAVITQu4vr4xnSDxMaL",   # Soft, friendly female
        "antoni": "ErXwobaYiN019PkySvjV",  # Well-rounded male
        "elli": "MF3mGyEYCl7XYWbV9V6O",    # Emotional, expressive female
        "josh": "TxGEqnHWrfWFTfGW9XjX",    # Young, energetic male
    }
    
    def __init__(self, api_key: str, default_voice: str = "rachel"):
        """
        Initialize ElevenLabs client
        
        Args:
            api_key: ElevenLabs API key
            default_voice: Default voice ID or preset name
        """
        self.client = ElevenLabs(api_key=api_key)
        self.default_voice = self._resolve_voice(default_voice)
        self.total_characters = 0
        
        logger.info(f"Initialized ElevenLabs client with voice: {default_voice}")
    
    def _resolve_voice(self, voice: str) -> str:
        """
        Resolve voice name to ID
        
        Args:
            voice: Voice ID or preset name
            
        Returns:
            Voice ID
        """
        if voice.lower() in self.VOICE_PRESETS:
            return self.VOICE_PRESETS[voice.lower()]
        return voice
    
# In commercial/clients/elevenlabs_client.py

    def generate_speech(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> Path:
        """
        Generate speech from text using the modern ElevenLabs SDK.
        """
        voice_id = self._resolve_voice(voice) if voice else self.default_voice
        
        logger.info(f"Generating speech: {len(text)} chars, voice={voice_id}")
        
        try:
            # Configure voice settings
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )
            
            # --- THIS IS THE CORRECTED CODE ---
            # The new SDK uses client.text_to_speech.convert()
            audio_stream = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=voice_settings,
            )
            
            # Save the streamed audio to a file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in audio_stream:
                    f.write(chunk)
            # --- END OF CORRECTION ---

            # Track character usage
            self.total_characters += len(text)
            
            logger.info(f"✅ Speech generated: {output_path.name}")
            return output_path
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}", exc_info=True)
            raise RuntimeError(f"ElevenLabs synthesis failed: {e}")
    
    def generate_batch(
        self,
        texts: List[str],
        output_dir: Path,
        voice: Optional[str] = None,
        prefix: str = "narration"
    ) -> List[Path]:
        """
        Generate multiple audio files
        
        Args:
            texts: List of text strings
            output_dir: Directory to save files
            voice: Voice ID or preset
            prefix: Filename prefix
            
        Returns:
            List of generated file paths
        """
        logger.info(f"Generating batch: {len(texts)} files")
        
        output_paths = []
        
        for i, text in enumerate(texts, 1):
            output_path = output_dir / f"{prefix}_{i:02d}.mp3"
            
            try:
                self.generate_speech(
                    text=text,
                    output_path=output_path,
                    voice=voice
                )
                output_paths.append(output_path)
                
            except Exception as e:
                logger.error(f"Failed to generate file {i}: {e}")
                # Continue with next file
        
        logger.info(f"✅ Batch complete: {len(output_paths)}/{len(texts)} files")
        return output_paths
    
    def list_voices(self) -> List[dict]:
        """
        List available voices
        
        Returns:
            List of voice metadata
        """
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "voice_id": v.voice_id,
                    "name": v.name,
                    "category": v.category,
                    "description": v.description
                }
                for v in voices.voices
            ]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []
    
    def get_cost_estimate(self) -> float:
        """
        Estimate cost based on character usage
        
        ElevenLabs pricing (as of 2024):
        - Starter: $5/month for 30,000 characters
        - Creator: $22/month for 100,000 characters
        - Pro: $99/month for 500,000 characters
        
        Average: ~$0.30 per 1,000 characters
        
        Returns:
            Estimated cost in USD
        """
        cost_per_thousand = 0.30
        return (self.total_characters / 1000) * cost_per_thousand
    
    def reset_usage(self):
        """Reset character counter"""
        self.total_characters = 0
        logger.debug("Reset character usage counter")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv(".env.commercial")
    
    client = ElevenLabsClient(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        default_voice="rachel"
    )
    
    # Generate single file
    output = client.generate_speech(
        text="Welcome to the future of AI video generation. This is a professional voiceover.",
        output_path=Path("test_voice.mp3")
    )
    
    print(f"\n🎙️  Audio: {output}")
    print(f"💰 Cost: ${client.get_cost_estimate():.4f}")
    
    # List available voices
    print("\n📋 Available voices:")
    for voice in client.list_voices()[:5]:
        print(f"  - {voice['name']} ({voice['category']})")
