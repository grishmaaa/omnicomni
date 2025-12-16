"""
TEST SCRIPT - Verify pipeline works
Run this to test if generation actually works
"""

from pathlib import Path
import sys

# Add path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("TESTING AI VIDEO GENERATOR PIPELINE")
print("=" * 70)
print()

# Test topic
topic = "The Future of Renewable Energy"

print(f"Topic: {topic}")
print()

try:
    # Import modules
    import importlib.util
    
    def import_mod(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    
    src = Path(__file__).parent / "src"
    
    # Step 1
    print("Step 1: Generating script...")
    script_gen = import_mod("script_gen", src / "1_script_gen.py")
    script_gen.generate_script(topic=topic, num_scenes=5, style="cinematic")
    print("✅ Script done\n")
    
    # Step 2
    print("Step 2: Generating images...")
    image_gen = import_mod("image_gen", src / "2_image_gen.py")
    image_gen.generate_images()
    print("✅ Images done\n")
    
    # Step 3
    print("Step 3: Generating videos (this takes 5-8 min)...")
    video_gen = import_mod("video_gen", src / "3_video_gen.py")
    video_gen.generate_videos()
    print("✅ Videos done\n")
    
    # Step 4
    print("Step 4: Generating audio...")
    audio_gen = import_mod("audio_gen", src / "4_audio_gen.py")
    audio_gen.generate_audio()
    print("✅ Audio done\n")
    
    # Step 5
    print("Step 5: Assembling final video...")
    assembler = import_mod("assembler", Path(__file__).parent / "complete_assembler.py")
    assembler.main()
    print("✅ Assembly done\n")
    
    print("=" * 70)
    print("SUCCESS! Check assets/FINAL_VIDEO.mp4")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
