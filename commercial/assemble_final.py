"""
Final video assembly - Step 5 only
Run this after quick_test.py completes
"""

import sys
from pathlib import Path
import importlib.util

def import_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

src_dir = Path(__file__).parent / "src"

print("=" * 70)
print("🎬 FINAL VIDEO ASSEMBLY")
print("=" * 70)
print()
print("Assembling final video from generated assets...")
print("⏳ This may take several minutes...")
print()

try:
    editor_mod = import_module_from_path("editor", src_dir / "5_editor.py")
    output_path = editor_mod.edit_video()
    
    print()
    print("=" * 70)
    print("🎉 SUCCESS! Final video ready!")
    print("=" * 70)
    print()
    print(f"📹 Output: {output_path}")
    print()
    print("You can now watch and publish your video!")
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
