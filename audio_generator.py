"""
Audio Generator using edge-tts
Converts scene JSON to audio files with proper naming conventions
"""

import asyncio
import edge_tts
import os
from typing import List, Dict, Any
from pathlib import Path
import re


class AudioGenerator:
    def __init__(self, output_dir: str = "audio_output"):
        """
        Initialize the audio generator
        
        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Voice mapping for different emotions and speakers
        self.voice_map = {
            "neutral": "en-US-ChristopherNeural",
            "excited": "en-US-JennyNeural",
            "serious": "en-GB-RyanNeural",
            "mysterious": "en-US-GuyNeural",
            "dramatic": "en-US-AriaNeural",
            "narrator": "en-US-ChristopherNeural",
            "host": "en-US-JennyNeural",
            "default": "en-US-ChristopherNeural"
        }
    
    def get_voice_for_scene(self, scene: Dict[str, Any]) -> str:
        """
        Select appropriate voice based on emotion and speaker
        
        Args:
            scene: Scene dictionary with speaker and emotion
            
        Returns:
            Voice name for edge-tts
        """
        emotion = scene.get("emotion", "neutral").lower()
        speaker = scene.get("speaker", "").lower()
        
        # First try to match by emotion
        if emotion in self.voice_map:
            return self.voice_map[emotion]
        
        # Then try to match by speaker
        if speaker in self.voice_map:
            return self.voice_map[speaker]
        
        # Default voice
        return self.voice_map["default"]
    
    def sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Create a safe filename from text
        
        Args:
            text: Text to convert to filename
            max_length: Maximum length of filename
            
        Returns:
            Sanitized filename
        """
        # Remove special characters
        safe_text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with underscores
        safe_text = re.sub(r'[\s]+', '_', safe_text)
        # Truncate if too long
        safe_text = safe_text[:max_length]
        # Remove trailing underscores
        safe_text = safe_text.strip('_')
        
        return safe_text.lower()
    
    def get_audio_filename(self, scene: Dict[str, Any], topic_slug: str = "") -> str:
        """
        Generate filename for audio file with naming convention:
        {topic_slug}_scene{number}_{speaker}_{emotion}.mp3
        
        Args:
            scene: Scene dictionary
            topic_slug: Sanitized topic name
            
        Returns:
            Filename for the audio file
        """
        scene_num = scene.get("scene_number", 0)
        speaker = self.sanitize_filename(scene.get("speaker", "unknown"))
        emotion = self.sanitize_filename(scene.get("emotion", "neutral"))
        
        if topic_slug:
            filename = f"{topic_slug}_scene{scene_num:02d}_{speaker}_{emotion}.mp3"
        else:
            filename = f"scene{scene_num:02d}_{speaker}_{emotion}.mp3"
        
        return filename
    
    async def generate_audio_for_scene(self, scene: Dict[str, Any], output_path: str) -> bool:
        """
        Generate audio file for a single scene
        
        Args:
            scene: Scene dictionary with text and metadata
            output_path: Full path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            text = scene.get("text", "")
            if not text:
                print(f"Warning: Scene {scene.get('scene_number')} has no text")
                return False
            
            voice = self.get_voice_for_scene(scene)
            
            print(f"  Generating: {Path(output_path).name}")
            print(f"    Voice: {voice}")
            print(f"    Text: {text[:60]}...")
            
            # Create TTS communication
            communicate = edge_tts.Communicate(text, voice)
            
            # Save to file
            await communicate.save(output_path)
            
            print(f"  ✓ Saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error generating audio for scene {scene.get('scene_number')}: {e}")
            return False
    
    async def generate_all_audio(self, scenes: List[Dict[str, Any]], topic: str = "") -> List[str]:
        """
        Generate audio files for all scenes
        
        Args:
            scenes: List of scene dictionaries
            topic: Topic name for filename prefix
            
        Returns:
            List of generated audio file paths
        """
        print(f"\n{'='*60}")
        print(f"Generating Audio Files")
        print(f"{'='*60}\n")
        
        # Create topic slug for filenames
        topic_slug = self.sanitize_filename(topic) if topic else ""
        
        # Create subdirectory for this topic
        if topic_slug:
            topic_dir = self.output_dir / topic_slug
            topic_dir.mkdir(exist_ok=True)
        else:
            topic_dir = self.output_dir
        
        print(f"Output directory: {topic_dir}\n")
        
        # Generate audio for each scene
        generated_files = []
        tasks = []
        
        for scene in scenes:
            filename = self.get_audio_filename(scene, topic_slug)
            output_path = str(topic_dir / filename)
            
            # Create async task
            task = self.generate_audio_for_scene(scene, output_path)
            tasks.append((task, output_path))
        
        # Run all tasks concurrently
        for task, output_path in tasks:
            success = await task
            if success:
                generated_files.append(output_path)
        
        print(f"\n{'='*60}")
        print(f"✓ Generated {len(generated_files)} audio files")
        print(f"{'='*60}\n")
        
        return generated_files
    
    def generate_audio_sync(self, scenes: List[Dict[str, Any]], topic: str = "") -> List[str]:
        """
        Synchronous wrapper for generate_all_audio
        
        Args:
            scenes: List of scene dictionaries
            topic: Topic name for filename prefix
            
        Returns:
            List of generated audio file paths
        """
        return asyncio.run(self.generate_all_audio(scenes, topic))


async def list_available_voices():
    """List all available edge-tts voices"""
    voices = await edge_tts.list_voices()
    
    print("\nAvailable English Voices:")
    print("="*60)
    
    en_voices = [v for v in voices if v['Locale'].startswith('en-')]
    
    for voice in en_voices[:20]:  # Show first 20
        print(f"{voice['ShortName']}")
        print(f"  Gender: {voice['Gender']}, Locale: {voice['Locale']}")
    
    print(f"\n... and {len(en_voices) - 20} more English voices")


if __name__ == "__main__":
    # Test the audio generator
    import json
    
    # Example scenes
    test_scenes = [
        {
            "scene_number": 1,
            "speaker": "Narrator",
            "text": "Deep in the Amazon rainforest, an archaeological team made a discovery that would change everything.",
            "emotion": "mysterious"
        },
        {
            "scene_number": 2,
            "speaker": "Dr. Sarah Chen",
            "text": "This artifact... it's unlike anything we've ever seen. The symbols don't match any known civilization.",
            "emotion": "excited"
        },
        {
            "scene_number": 3,
            "speaker": "Professor James",
            "text": "We must proceed with extreme caution. Some discoveries are meant to remain hidden.",
            "emotion": "serious"
        }
    ]
    
    # Generate audio
    generator = AudioGenerator()
    audio_files = generator.generate_audio_sync(
        test_scenes, 
        topic="ancient_artifact_discovery"
    )
    
    print("\nGenerated files:")
    for file in audio_files:
        print(f"  - {file}")
    
    # Optionally list available voices
    # asyncio.run(list_available_voices())
