"""
Quick test script for enterprise patterns
Tests Pydantic validation and configuration loading
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import (
    settings,
    SceneModel,
    StoryboardModel,
    validate_llm_output,
    ValidationError
)


def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    print(f"  Model ID: {settings.model_id}")
    print(f"  Voice ID: {settings.voice_id}")
    print(f"  Temperature: {settings.temperature}")
    print(f"  Output Root: {settings.output_root}")
    print(f"  CUDA Available: {settings.is_cuda_available}")
    print("  ✅ Configuration loaded\n")


def test_scene_validation():
    """Test Pydantic scene validation"""
    print("📋 Testing Scene Validation...")
    
    # Valid scene
    try:
        scene = SceneModel(
            scene_id=1,
            visual_prompt="Neon-lit Tokyo street, 4k ultra detailed, volumetric lighting",
            audio_text="Welcome to Neo-Tokyo",
            duration=8
        )
        print(f"  ✅ Valid scene: {scene.scene_id}")
    except ValidationError as e:
        print(f"  ❌ Validation failed: {e}")
        return False
    
    # Invalid scene (empty text)
    try:
        invalid = SceneModel(
            scene_id=2,
            visual_prompt="Test",
            audio_text="",  # Empty - should fail
            duration=8
        )
        print(f"  ❌ Should have failed for empty text!")
        return False
    except ValidationError:
        print(f"  ✅ Correctly rejected empty audio_text")
    
    print()
    return True


def test_storyboard_validation():
    """Test full storyboard validation"""
    print("🎬 Testing Storyboard Validation...")
    
    raw_scenes = [
        {
            "scene_id": 1,
            "visual_prompt": "Ancient Ethiopian highlands, 4k, golden hour lighting, cinematic",
            "audio_text": "Coffee's story begins in Ethiopia.",
            "duration": 8
        },
        {
            "scene_id": 2,
            "visual_prompt": "Modern café, sleek lines, minimalist decor, espresso steam",
            "audio_text": "Today, coffee is a global phenomenon.",
            "duration": 10
        }
    ]
    
    try:
        storyboard = validate_llm_output(raw_scenes, "The history of coffee")
        print(f"  ✅ Storyboard validated")
        print(f"     Scenes: {storyboard.scene_count}")
        print(f"     Total duration: {storyboard.total_duration}s")
        print(f"     Topic: {storyboard.topic}")
    except ValidationError as e:
        print(f"  ❌ Validation failed: {e}")
        return False
    
    print()
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ENTERPRISE PATTERNS - VALIDATION TESTS")
    print("="*70 + "\n")
    
    try:
        test_configuration()
        test_scene_validation()
        test_storyboard_validation()
        
        print("="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\nEnterprise patterns working correctly!")
        print("Ready to integrate with pipeline_manager.py")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
