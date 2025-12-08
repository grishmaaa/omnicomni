"""
Quick Demo - Generate Audio from Custom Scenes
Works immediately without model access!
"""

from audio_generator import AudioGenerator
import json
from pathlib import Path

def create_custom_scenes(topic: str) -> list:
    """
    Create your own custom scenes here!
    Edit this function to create any story you want.
    """
    
    # Example: Space Signal Story
    if "space" in topic.lower() or "signal" in topic.lower():
        return [
            {
                "scene_number": 1,
                "speaker": "Narrator",
                "text": "In the depths of space, Earth's radio telescopes detected something extraordinary. A signal, repeating every 47 seconds, coming from beyond our solar system.",
                "emotion": "mysterious"
            },
            {
                "scene_number": 2,
                "speaker": "Dr. Sarah Chen",
                "text": "This is it! This is what we've been searching for! The pattern is too complex to be natural. Someone is trying to communicate with us!",
                "emotion": "excited"
            },
            {
                "scene_number": 3,
                "speaker": "Commander Hayes",
                "text": "Alert all international space agencies. We need to assemble the best minds on the planet. This changes everything.",
                "emotion": "serious"
            },
            {
                "scene_number": 4,
                "speaker": "Dr. Sarah Chen",
                "text": "I've decoded part of the message. It's coordinates... and they're pointing to a location just outside our galaxy.",
                "emotion": "excited"
            },
            {
                "scene_number": 5,
                "speaker": "Narrator",
                "text": "As humanity prepared its response, one question remained: were we ready to answer the call from the stars?",
                "emotion": "dramatic"
            }
        ]
    
    # Default story template
    return [
        {
            "scene_number": 1,
            "speaker": "Narrator",
            "text": f"Our story begins with an exploration of {topic}.",
            "emotion": "neutral"
        },
        {
            "scene_number": 2,
            "speaker": "Expert",
            "text": f"The fascinating thing about {topic} is how it connects to so many aspects of our world.",
            "emotion": "excited"
        },
        {
            "scene_number": 3,
            "speaker": "Narrator",
            "text": f"And that's the story of {topic}. Thank you for listening.",
            "emotion": "neutral"
        }
    ]


def main():
    print("\n" + "="*70)
    print(" "*20 + "CUSTOM AUDIO DEMO")
    print("="*70)
    print("\nCreate audio scenes without waiting for AI model access!")
    print("Edit the create_custom_scenes() function to make your own stories.\n")
    
    # Get topic
    topic = input("Enter your topic (or press Enter for default): ").strip()
    if not topic:
        topic = "A mysterious signal from deep space"
    
    # Create scenes
    print(f"\nCreating scenes for: {topic}")
    scenes = create_custom_scenes(topic)
    
    # Show scenes
    print("\n" + "-"*70)
    print("SCENES:")
    print("-"*70)
    for scene in scenes:
        print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
        print(f"  \"{scene['text']}\"")
    
    # Generate audio
    print("\n" + "-"*70)
    print("GENERATING AUDIO...")
    print("-"*70)
    
    generator = AudioGenerator(output_dir="demo_output")
    audio_files = generator.generate_audio_sync(scenes, topic)
    
    # Save scenes
    output_dir = Path("demo_output") / generator.sanitize_filename(topic)
    scenes_file = output_dir / "scenes.json"
    with open(scenes_file, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "="*70)
    print("SUCCESS!")
    print("="*70)
    print(f"\n📁 Output folder: {output_dir}")
    print(f"📝 Scenes: {len(scenes)}")
    print(f"🔊 Audio files: {len(audio_files)}")
    print("\n🎵 Generated files:")
    for file in audio_files:
        print(f"  ✓ {Path(file).name}")
    
    print(f"\n📄 Scenes saved to: {scenes_file}")
    print("\n" + "="*70)
    print("\n💡 TIP: Edit create_custom_scenes() in this file to create")
    print("   your own custom stories with any topic!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
