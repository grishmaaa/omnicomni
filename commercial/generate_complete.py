"""
COMPLETE AI VIDEO GENERATOR
One command to generate top-notch quality videos
"""

import sys
from pathlib import Path
import importlib.util

def import_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    """Complete AI video generation pipeline"""
    
    print("=" * 70)
    print("🤖 AI VIDEO GENERATOR - COMPLETE AUTOMATION")
    print("=" * 70)
    print()
    print("The AI will handle everything automatically:")
    print("  1. Generate screenplay")
    print("  2. Create HD images")
    print("  3. Generate videos")
    print("  4. Create voiceovers")
    print("  5. AI Assembly (Second Brain)")
    print()
    print("=" * 70)
    print()
    
    src_dir = Path(__file__).parent / "src"
    
    try:
        # Step 1: Script
        print("STEP 1/5: AI Scriptwriter...")
        print("-" * 70)
        script_gen = import_module_from_path("script_gen", src_dir / "1_script_gen.py")
        script_gen.generate_script(
            topic="The History of Espresso",  # Change this!
            num_scenes=5,
            style="cinematic"
        )
        print()
        
        # Step 2: Images
        print("STEP 2/5: AI Image Generator...")
        print("-" * 70)
        image_gen = import_module_from_path("image_gen", src_dir / "2_image_gen.py")
        image_gen.generate_images()
        print()
        
        # Step 3: Videos
        print("STEP 3/5: AI Video Generator...")
        print("-" * 70)
        print("⏳ This takes 2-5 minutes...")
        video_gen = import_module_from_path("video_gen", src_dir / "3_video_gen.py")
        video_gen.generate_videos()
        print()
        
        # Step 4: Audio
        print("STEP 4/5: AI Voice Generator...")
        print("-" * 70)
        audio_gen = import_module_from_path("audio_gen", src_dir / "4_audio_gen.py")
        audio_gen.generate_audio()
        print()
        
        # Step 5: AI Assembly
        print("STEP 5/5: AI Second Brain (Assembly)...")
        print("-" * 70)
        ai_assembler = import_module_from_path("ai_assembler", Path(__file__).parent / "ai_assembler.py")
        ai_assembler.main()
        
        print()
        print("=" * 70)
        print("🎉 COMPLETE! AI has created your video!")
        print("=" * 70)
        print()
        print("Your top-notch quality video is ready!")
        print("Location: commercial/assets/FINAL_VIDEO.mp4")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
