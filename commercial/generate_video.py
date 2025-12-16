"""
Simple CLI to run the full video generation pipeline
No Streamlit - just pure Python execution
"""

import os
import sys
from pathlib import Path

# Import modules using importlib (files start with numbers)
import importlib.util

def import_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = Path(__file__).parent / "src"
script_gen_mod = import_module_from_path("script_gen", src_dir / "1_script_gen.py")
image_gen_mod = import_module_from_path("image_gen", src_dir / "2_image_gen.py")
video_gen_mod = import_module_from_path("video_gen", src_dir / "3_video_gen.py")
audio_gen_mod = import_module_from_path("audio_gen", src_dir / "4_audio_gen.py")
editor_mod = import_module_from_path("editor", src_dir / "5_editor.py")

generate_script = script_gen_mod.generate_script
generate_images = image_gen_mod.generate_images
generate_videos = video_gen_mod.generate_videos
generate_audio = audio_gen_mod.generate_audio
edit_video = editor_mod.edit_video

def main():
    """Run the complete pipeline"""
    
    print("=" * 70)
    print("🎬 AI VIDEO GENERATOR - FULL PIPELINE")
    print("=" * 70)
    print()
    
    # Configuration
    TOPIC = "The History of Espresso"  # Change this!
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
        print("STEP 1/5: Generating screenplay...")
        print("-" * 70)
        screenplay = generate_script(
            topic=TOPIC,
            num_scenes=NUM_SCENES,
            style=STYLE
        )
        print("✅ Script generated!")
        print()
        
        # Step 2: Generate Images
        print("STEP 2/5: Generating images...")
        print("-" * 70)
        generate_images()
        print("✅ Images generated!")
        print()
        
        # Step 3: Generate Videos
        print("STEP 3/5: Generating videos...")
        print("-" * 70)
        print("⏳ This may take 30-60 seconds per scene...")
        generate_videos()
        print("✅ Videos generated!")
        print()
        
        # Step 4: Generate Audio
        print("STEP 4/5: Generating audio...")
        print("-" * 70)
        generate_audio()
        print("✅ Audio generated!")
        print()
        
        # Step 5: Edit Final Video
        print("STEP 5/5: Assembling final video...")
        print("-" * 70)
        print("⏳ This may take several minutes...")
        output_path = edit_video()
        print("✅ Video compiled!")
        print()
        
        # Success!
        print("=" * 70)
        print("🎉 SUCCESS! Video generation complete!")
        print("=" * 70)
        print()
        print(f"📹 Output: {output_path}")
        print()
        print("You can now:")
        print("  1. Watch the video")
        print("  2. Upload to your platform")
        print("  3. Generate another video (edit TOPIC above)")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        print("Check that all API keys are set in .env.commercial")
        sys.exit(1)


if __name__ == "__main__":
    main()
