"""Test video generation with detailed error output"""
import sys
from pathlib import Path

# Add path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load dotenv
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env.commercial"
load_dotenv(env_path)

# Import module
import importlib.util
spec = importlib.util.spec_from_file_location("video_gen", Path(__file__).parent / "src" / "3_video_gen.py")
video_gen = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(video_gen)
    print("Module loaded successfully")
    
    # Call generate_videos
    video_gen.generate_videos()
    print("Videos generated!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
