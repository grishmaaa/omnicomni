"""
Complete Audio Scene Generation Pipeline
Input: Topic → JSON Scenes → Audio Files

This script orchestrates the entire pipeline:
1. Takes a topic as input
2. Generates JSON scenes using Llama-3.2-3B
3. Creates audio files using edge-tts
4. Saves everything with proper naming conventions
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from scene_generator import SceneGenerator
from audio_generator import AudioGenerator


class AudioScenePipeline:
    def __init__(self, output_base_dir: str = "output"):
        """
        Initialize the complete pipeline
        
        Args:
            output_base_dir: Base directory for all outputs
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        print("\n" + "="*70)
        print(" "*20 + "AUDIO SCENE PIPELINE")
        print("="*70)
        
        # Initialize components
        print("\n[1/3] Initializing Scene Generator...")
        self.scene_generator = SceneGenerator()
        
        print("\n[2/3] Initializing Audio Generator...")
        self.audio_generator = AudioGenerator(
            output_dir=str(self.output_base_dir / "audio")
        )
        
        print("\n[3/3] Pipeline ready!")
    
    def create_project_folder(self, topic: str) -> Path:
        """
        Create a timestamped project folder for this generation
        
        Args:
            topic: The topic being processed
            
        Returns:
            Path to the project folder
        """
        # Create safe folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = self.audio_generator.sanitize_filename(topic, max_length=30)
        folder_name = f"{timestamp}_{topic_slug}"
        
        project_folder = self.output_base_dir / folder_name
        project_folder.mkdir(exist_ok=True)
        
        return project_folder
    
    def run(self, topic: str, save_scenes: bool = True) -> dict:
        """
        Run the complete pipeline
        
        Args:
            topic: The topic to generate scenes about
            save_scenes: Whether to save the scenes JSON file
            
        Returns:
            Dictionary with results including scenes and audio file paths
        """
        print("\n" + "="*70)
        print(f"PROCESSING TOPIC: {topic}")
        print("="*70)
        
        # Create project folder
        project_folder = self.create_project_folder(topic)
        print(f"\nProject folder: {project_folder}")
        
        # Step 1: Generate scenes
        print("\n" + "-"*70)
        print("STEP 1: GENERATING SCENES")
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
        
        # Update audio generator to use project folder
        audio_folder = project_folder / "audio"
        audio_folder.mkdir(exist_ok=True)
        self.audio_generator.output_dir = audio_folder
        
        audio_files = self.audio_generator.generate_audio_sync(scenes, topic)
        
        # Create summary
        summary = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
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
        
        # Create README
        self._create_readme(project_folder, summary)
        
        # Final summary
        print("\n" + "="*70)
        print("PIPELINE COMPLETE!")
        print("="*70)
        print(f"\n📁 Project Folder: {project_folder}")
        print(f"📝 Scenes Generated: {len(scenes)}")
        print(f"🔊 Audio Files Created: {len(audio_files)}")
        print(f"\n📄 Files:")
        print(f"  - scenes.json (scene definitions)")
        print(f"  - summary.json (complete metadata)")
        print(f"  - README.md (human-readable summary)")
        print(f"  - audio/ (audio files)")
        
        print(f"\n🎵 Audio Files:")
        for audio_file in audio_files:
            print(f"  - {Path(audio_file).name}")
        
        print("\n" + "="*70 + "\n")
        
        return summary
    
    def _create_readme(self, project_folder: Path, summary: dict):
        """Create a human-readable README for the project"""
        readme_content = f"""# Audio Scene Generation Project

## Topic
{summary['topic']}

## Generated
{summary['timestamp']}

## Statistics
- **Scenes**: {summary['num_scenes']}
- **Audio Files**: {summary['num_audio_files']}

## Scenes

"""
        
        for scene in summary['scenes']:
            readme_content += f"""### Scene {scene['scene_number']}: {scene['speaker']}
- **Emotion**: {scene['emotion']}
- **Text**: "{scene['text']}"

"""
        
        readme_content += f"""## Audio Files

"""
        
        for audio_file in summary['audio_files']:
            filename = Path(audio_file).name
            readme_content += f"- `{filename}`\n"
        
        readme_content += f"""
## File Structure

```
{project_folder.name}/
├── scenes.json          # Scene definitions (JSON)
├── summary.json         # Complete metadata
├── README.md           # This file
└── audio/              # Generated audio files
    ├── *.mp3
    └── ...
```

## Usage

Play the audio files in order (scene01, scene02, etc.) to experience the complete audio drama.
"""
        
        readme_file = project_folder / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✓ README created: {readme_file}")


def main():
    """Main entry point with CLI support"""
    parser = argparse.ArgumentParser(
        description="Generate audio scenes from a topic using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py "The discovery of a mysterious ancient artifact"
  python pipeline.py "A day in the life of an astronaut on Mars" --output my_projects
  python pipeline.py "The last library on Earth" --no-save-scenes
        """
    )
    
    parser.add_argument(
        "topic",
        type=str,
        help="The topic to generate scenes about"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Base output directory (default: output)"
    )
    
    parser.add_argument(
        "--no-save-scenes",
        action="store_true",
        help="Don't save the scenes.json file"
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = AudioScenePipeline(output_base_dir=args.output)
    pipeline.run(
        topic=args.topic,
        save_scenes=not args.no_save_scenes
    )


if __name__ == "__main__":
    # If run without arguments, use interactive mode
    import sys
    
    if len(sys.argv) == 1:
        print("\n" + "="*70)
        print(" "*15 + "INTERACTIVE MODE")
        print("="*70)
        
        topic = input("\nEnter your topic: ").strip()
        
        if not topic:
            print("Error: Topic cannot be empty")
            sys.exit(1)
        
        pipeline = AudioScenePipeline()
        pipeline.run(topic)
    else:
        main()
