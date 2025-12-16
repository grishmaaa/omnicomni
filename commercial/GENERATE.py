"""
SIMPLE VIDEO GENERATOR - COMMAND LINE
Just run this and enter your topic!
"""

from pathlib import Path
import sys
import importlib.util

def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

print("=" * 70)
print("AI VIDEO GENERATOR")
print("=" * 70)
print()

# Get topic from user
topic = input("Enter your video topic: ").strip()

if not topic:
    print("Error: Please enter a topic!")
    sys.exit(1)

print()
print(f"Generating video about: {topic}")
print("This will take 10-15 minutes...")
print()

src = Path(__file__).parent / "src"

try:
    # Step 1
    print("Step 1/5: Writing script...")
    script_gen = load_mod("s1", src / "1_script_gen.py")
    script_gen.generate_script(topic=topic, num_scenes=5, style="cinematic")
    print("✅ Done\n")
    
    # Step 2
    print("Step 2/5: Creating images...")
    image_gen = load_mod("s2", src / "2_image_gen.py")
    image_gen.generate_images()
    print("✅ Done\n")
    
    # Step 3
    print("Step 3/5: Generating videos (5-8 min)...")
    video_gen = load_mod("s3", src / "3_video_gen.py")
    video_gen.generate_videos()
    print("✅ Done\n")
    
    # Step 4
    print("Step 4/5: Creating audio...")
    audio_gen = load_mod("s4", src / "4_audio_gen.py")
    audio_gen.generate_audio()
    print("✅ Done\n")
    
    # Step 5
    print("Step 5/5: Assembling final video...")
    assembler = load_mod("s5", Path(__file__).parent / "complete_assembler.py")
    assembler.main()
    print("✅ Done\n")
    
    print("=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print()
    print("Your video is ready:")
    print("  Location: commercial/assets/FINAL_VIDEO.mp4")
    print()
    print("You can now:")
    print("  1. Watch the video")
    print("  2. Download and share it")
    print("  3. Run this script again for more videos")
    print()
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
