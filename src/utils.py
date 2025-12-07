"""
Utility functions for the audio scene generation pipeline
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json


def create_project_folder(base_dir: Path, topic: str) -> Path:
    """
    Create timestamped project folder
    
    Args:
        base_dir: Base output directory
        topic: Topic name
        
    Returns:
        Path to created project folder
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = sanitize_for_folder(topic)
    folder_name = f"{timestamp}_{topic_slug}"
    
    project_folder = base_dir / folder_name
    project_folder.mkdir(parents=True, exist_ok=True)
    
    return project_folder


def sanitize_for_folder(text: str, max_length: int = 30) -> str:
    """Create safe folder name from text"""
    import re
    safe = re.sub(r'[^\w\s-]', '', text)
    safe = re.sub(r'[\s]+', '_', safe)
    safe = safe[:max_length].strip('_').lower()
    return safe or "untitled"


def save_project_metadata(
    project_folder: Path,
    topic: str,
    scenes: List[Dict[str, Any]],
    audio_files: List[str],
    model_name: str
) -> None:
    """Save complete project metadata"""
    
    # Save scenes
    scenes_file = project_folder / "scenes.json"
    with open(scenes_file, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)
    
    # Save summary
    summary = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "num_scenes": len(scenes),
        "num_audio_files": len(audio_files),
        "scenes": scenes,
        "audio_files": audio_files
    }
    
    summary_file = project_folder / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Create README
    create_project_readme(project_folder, summary)
    
    print(f"📄 Metadata saved to {project_folder}")


def create_project_readme(project_folder: Path, summary: Dict[str, Any]) -> None:
    """Generate README for the project"""
    
    readme_content = f"""# Audio Scene Project

## Topic
{summary['topic']}

## Generated
{summary['timestamp']}

## Model
{summary['model']}

## Statistics
- Scenes: {summary['num_scenes']}
- Audio Files: {summary['num_audio_files']}

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
    
    readme_file = project_folder / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def print_scenes(scenes: List[Dict[str, Any]]) -> None:
    """Pretty print scenes to console"""
    print(f"\n{'='*60}")
    print("GENERATED SCENES")
    print(f"{'='*60}")
    
    for scene in scenes:
        print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
        print(f"  \"{scene['text']}\"")
    
    print(f"\n{'='*60}\n")
