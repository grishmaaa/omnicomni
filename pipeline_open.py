"""
Pipeline using Open Model (Llama-3.2-1B)
No access request required!
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from scene_generator_open import SceneGeneratorOpen
from audio_generator import AudioGenerator


class AudioScenePipelineOpen:
    def __init__(self, output_base_dir: str = "output"):
        """Initialize the pipeline with open model"""
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        print("\n" + "="*70)
        print(" "*15 + "AUDIO SCENE PIPELINE (OPEN MODEL)")
        print("="*70)
        print("\nUsing Llama-3.2-1B - No access request needed!")
        
        # Initialize components
        print("\n[1/3] Initializing Scene Generator...")
        self.scene_generator = SceneGeneratorOpen()
        
        print("\n[2/3] Initializing Audio Generator...")
        self.audio_generator = AudioGenerator(
            output_dir=str(self.output_base_dir / "audio")
        )
        
        print("\n[3/3] Pipeline ready!")
    
    def create_project_folder(self, topic: str) -> Path:
        """Create a timestamped project folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = self.audio_generator.sanitize_filename(topic, max_length=30)
        folder_name = f"{timestamp}_{topic_slug}"
        
        project_folder = self.output_base_dir / folder_name
        project_folder.mkdir(exist_ok=True)
        
        return project_folder
    
    def run(self, topic: str, save_scenes: bool = True) -> dict:
        """Run the complete pipeline"""
        print("\n" + "="*70)
        print(f"PROCESSING TOPIC: {topic}")
        print("="*70)
        
        # Create project folder
        project_folder = self.create_project_folder(topic)
        print(f"\nProject folder: {project_folder}")
        
        # Step 1: Generate scenes
        print("\n" + "-"*70)
        print("STEP 1: GENERATING SCENES WITH AI")
        print("-"*70)
        
        scenes = self.scene_generator.generate_scenes(topic)
        
        # Save scenes JSON
        if save_scenes:
            scenes_file = project_folder / "scenes.json"
            with open(scenes_file, 'w', encoding='utf-8') as f:
                json.dump(scenes, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Scenes saved to: {scenes_file}")
        
        # Print scenes
        print("\n" + "-"*70)
        print("GENERATED SCENES:")
        print("-"*70)
        for scene in scenes:
            print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
            print(f"  \"{scene['text']}\"")
        
        # Step 2: Generate audio
        print("\n" + "-"*70)
        print("STEP 2: GENERATING AUDIO FILES")
        print("-"*70)
        
        audio_folder = project_folder / "audio"
        audio_folder.mkdir(exist_ok=True)
        self.audio_generator.output_dir = audio_folder
        
        audio_files = self.audio_generator.generate_audio_sync(scenes, topic)
        
        # Create summary
        summary = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "model": "Llama-3.2-1B (Open Access)",
            "project_folder": str(project_folder),
            "num_scenes": len(scenes),
            "num_audio_files": len(audio_files),
            "scenes": scenes,
            "audio_files": audio_files
        }
        
        # Save summary
        summary_file = project_folder / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Final summary
        print("\n" + "="*70)
        print("PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📁 Project Folder: {project_folder}")
        print(f"📝 Scenes Generated: {len(scenes)}")
        print(f"🔊 Audio Files Created: {len(audio_files)}")
        print(f"\n🎵 Audio Files:")
        for audio_file in audio_files:
            print(f"  - {Path(audio_file).name}")
        
        print("\n" + "="*70 + "\n")
        
        return summary


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        print("\n" + "="*70)
        print(" "*15 + "INTERACTIVE MODE")
        print("="*70)
        
        topic = input("\nEnter your topic: ").strip()
        
        if not topic:
            print("Error: Topic cannot be empty")
            sys.exit(1)
        
        pipeline = AudioScenePipelineOpen()
        pipeline.run(topic)
    else:
        topic = sys.argv[1]
        pipeline = AudioScenePipelineOpen()
        pipeline.run(topic)
