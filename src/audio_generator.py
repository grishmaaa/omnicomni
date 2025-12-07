"""
Audio Generator using edge-tts
Converts scene JSON to audio files with emotion-based voice selection
"""

import asyncio
import edge_tts
from typing import List, Dict, Any
from pathlib import Path
import re


class AudioGenerator:
    """Generates audio files from scene descriptions"""
    
    # Voice mappings for different emotions
    VOICE_MAP = {
        "neutral": "en-US-ChristopherNeural",
        "excited": "en-US-JennyNeural",
        "serious": "en-GB-RyanNeural",
        "mysterious": "en-US-GuyNeural",
        "dramatic": "en-US-AriaNeural",
        "default": "en-US-ChristopherNeural"
    }
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize audio generator
        
        Args:
            output_dir: Base directory for audio output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_audio_sync(
        self, 
        scenes: List[Dict[str, Any]], 
        topic: str = "",
        project_name: str = ""
    ) -> List[str]:
        """
        Generate audio files synchronously
        
        Args:
            scenes: List of scene dictionaries
            topic: Topic name for file naming
            project_name: Custom project name (optional)
            
        Returns:
            List of generated audio file paths
        """
        return asyncio.run(self.generate_audio(scenes, topic, project_name))
    
    async def generate_audio(
        self,
        scenes: List[Dict[str, Any]],
        topic: str = "",
        project_name: str = ""
    ) -> List[str]:
        """Generate audio files asynchronously"""
        print(f"🎵 Generating audio for {len(scenes)} scenes...")
        
        # Create topic-specific directory
        topic_slug = self._sanitize_filename(project_name or topic)
        audio_dir = self.output_dir / topic_slug
        audio_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"📁 Output directory: {audio_dir}\n")
        
        # Generate all audio files
        generated_files = []
        
        for scene in scenes:
            filename = self._get_audio_filename(scene, topic_slug)
            output_path = audio_dir / filename
            
            success = await self._generate_scene_audio(scene, str(output_path))
            if success:
                generated_files.append(str(output_path))
        
        print(f"\n✅ Generated {len(generated_files)} audio files!\n")
        return generated_files
    
    async def _generate_scene_audio(self, scene: Dict[str, Any], output_path: str) -> bool:
        """Generate audio for a single scene"""
        try:
            text = scene.get("text", "")
            if not text:
                print(f"⚠️  Scene {scene.get('scene_number')} has no text")
                return False
            
            voice = self._get_voice_for_scene(scene)
            
            print(f"  🎤 Scene {scene.get('scene_number')}: {scene.get('speaker')} ({voice})")
            print(f"     \"{text[:60]}...\"" if len(text) > 60 else f"     \"{text}\"")
            
            # Generate audio
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
            print(f"  ✅ Saved: {Path(output_path).name}\n")
            return True
            
        except Exception as e:
            print(f"  ❌ Error generating scene {scene.get('scene_number')}: {e}\n")
            return False
    
    def _get_voice_for_scene(self, scene: Dict[str, Any]) -> str:
        """Select voice based on emotion and speaker"""
        emotion = scene.get("emotion", "neutral").lower()
        speaker = scene.get("speaker", "").lower()
        
        # Match by emotion first
        if emotion in self.VOICE_MAP:
            return self.VOICE_MAP[emotion]
        
        # Match by speaker keyword
        if speaker in self.VOICE_MAP:
            return self.VOICE_MAP[speaker]
        
        return self.VOICE_MAP["default"]
    
    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """Create safe filename from text"""
        safe_text = re.sub(r'[^\w\s-]', '', text)
        safe_text = re.sub(r'[\s]+', '_', safe_text)
        safe_text = safe_text[:max_length]
        safe_text = safe_text.strip('_')
        return safe_text.lower() or "untitled"
    
    def _get_audio_filename(self, scene: Dict[str, Any], topic_slug: str) -> str:
        """Generate filename: {topic}_scene{XX}_{speaker}_{emotion}.mp3"""
        scene_num = scene.get("scene_number", 0)
        speaker = self._sanitize_filename(scene.get("speaker", "unknown"))
        emotion = self._sanitize_filename(scene.get("emotion", "neutral"))
        
        return f"{topic_slug}_scene{scene_num:02d}_{speaker}_{emotion}.mp3"
