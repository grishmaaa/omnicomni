"""
Test Audio Generation Only
Tests edge-tts without requiring Llama model access
"""

from audio_generator import AudioGenerator
import json

# Example scenes (manually created, no AI needed)
test_scenes = [
    {
        "scene_number": 1,
        "speaker": "Narrator",
        "text": "Deep in space, a mysterious signal was detected by Earth's most powerful telescopes.",
        "emotion": "mysterious"
    },
    {
        "scene_number": 2,
        "speaker": "Dr. Sarah Chen",
        "text": "This is incredible! The pattern repeats every 47 seconds. It's definitely artificial!",
        "emotion": "excited"
    },
    {
        "scene_number": 3,
        "speaker": "Commander Hayes",
        "text": "Alert the international space council immediately. This changes everything we know.",
        "emotion": "serious"
    },
    {
        "scene_number": 4,
        "speaker": "Narrator",
        "text": "As the world watched, humanity prepared to answer the call from the stars.",
        "emotion": "dramatic"
    }
]

print("\n" + "="*70)
print(" "*15 + "AUDIO GENERATION TEST")
print("="*70)
print("\nThis test generates audio from pre-made scenes.")
print("No AI model required - just testing edge-tts!\n")

# Generate audio
generator = AudioGenerator(output_dir="test_output")
audio_files = generator.generate_audio_sync(
    test_scenes, 
    topic="mysterious_space_signal"
)

print("\n" + "="*70)
print("SUCCESS! Audio files generated:")
print("="*70)
for file in audio_files:
    print(f"  ✓ {file}")

print("\n" + "="*70)
print("Check the 'test_output' folder to listen to your audio files!")
print("="*70 + "\n")

# Save scenes for reference
with open("test_output/test_scenes.json", "w", encoding="utf-8") as f:
    json.dump(test_scenes, f, indent=2, ensure_ascii=False)

print("Scenes saved to: test_output/test_scenes.json\n")
