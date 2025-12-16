"""
Simple CLI to run video generation (Steps 1-4)
Skips final assembly for now - generates script, images, videos, and audio
"""

import os
import sys
from pathlib import Path
import importlib.util

def import_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = Path(__file__).parent / "src"

def main():
    """Run pipeline steps 1-4"""
    
    print("=" * 70)
    print("🎬 AI VIDEO GENERATOR - QUICK TEST")
    print("=" * 70)
    print()
    
    # Configuration
    TOPIC = "The History of Espresso"
    NUM_SCENES = 5
    STYLE = "cinematic"
    
    print(f"📝 Topic: {TOPIC}")
    print(f"🎨 Style: {STYLE}")
    print(f"🎬 Scenes: {NUM_SCENES}")
    print()
    print("=" * 70)
    print()
    
    try:
        # Step 1: Generate Script
        print("STEP 1/4: Generating screenplay...")
        print("-" * 70)
        script_gen_mod = import_module_from_path("script_gen", src_dir / "1_script_gen.py")
        screenplay = script_gen_mod.generate_script(
            topic=TOPIC,
            num_scenes=NUM_SCENES,
            style=STYLE
        )
        print("✅ Script generated!")
        print()
        
        # Step 2: Generate Images
        print("STEP 2/4: Generating images...")
        print("-" * 70)
        image_gen_mod = import_module_from_path("image_gen", src_dir / "2_image_gen.py")
        image_gen_mod.generate_images()
        print("✅ Images generated!")
        print()
        
        # Step 3: Generate Videos
        print("STEP 3/4: Generating videos...")
        print("-" * 70)
        print("⏳ This may take 30-60 seconds per scene...")
        video_gen_mod = import_module_from_path("video_gen", src_dir / "3_video_gen.py")
        video_gen_mod.generate_videos()
        print("✅ Videos generated!")
        print()
        
        # Step 4: Generate Audio
        print("STEP 4/4: Generating audio...")
        print("-" * 70)
        audio_gen_mod = import_module_from_path("audio_gen", src_dir / "4_audio_gen.py")
        audio_gen_mod.generate_audio()
        print("✅ Audio generated!")
        print()
        
        # Success!
        print("=" * 70)
        print("🎉 SUCCESS! Media generation complete!")
        print("=" * 70)
        print()
        print("Generated files:")
        print("  📄 Script: commercial/script.json")
        print("  🖼️  Images: commercial/assets/images/")
        print("  🎬 Videos: commercial/assets/videos/")
        print("  🎙️  Audio: commercial/assets/audio/")
        print()
        print("Next: Install moviepy to assemble final video")
        print("  pip install moviepy")
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
