"""Make src modules importable"""
from pathlib import Path
import importlib.util

def load_module(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

src_dir = Path(__file__).parent

script_gen_module = load_module("script_gen", src_dir / "1_script_gen.py")
image_gen_module = load_module("image_gen", src_dir / "2_image_gen.py")
video_gen_module = load_module("video_gen", src_dir / "3_video_gen.py")
audio_gen_module = load_module("audio_gen", src_dir / "4_audio_gen.py")
