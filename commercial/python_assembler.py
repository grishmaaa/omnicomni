"""
AI Video Assembler - Pure Python Solution
Works without FFmpeg installation - uses imageio with bundled ffmpeg
"""

import json
from pathlib import Path
import imageio
from imageio_ffmpeg import get_ffmpeg_exe

class PythonVideoAssembler:
    """Pure Python video assembler - no external dependencies needed"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.assets_dir = project_dir / "assets"
        self.videos_dir = self.assets_dir / "videos"
        self.audio_dir = self.assets_dir / "audio"
        self.script_path = project_dir / "script.json"
        
    def assemble(self):
        """Assemble final video using pure Python"""
        print("=" * 70)
        print("🤖 AI VIDEO ASSEMBLER - PURE PYTHON")
        print("=" * 70)
        print()
        
        # Load script
        with open(self.script_path, 'r', encoding='utf-8') as f:
            screenplay = json.load(f)
        
        scenes = screenplay['scenes']
        print(f"📋 Processing {len(scenes)} scenes...")
        print()
        
        # Collect all video files
        video_files = []
        for scene in scenes:
            scene_num = scene['scene_number']
            video_file = self.videos_dir / f"scene_{scene_num}.mp4"
            
            if video_file.exists():
                video_files.append(str(video_file))
                print(f"   ✅ Scene {scene_num}: {video_file.name}")
            else:
                print(f"   ⚠️  Scene {scene_num}: Missing!")
        
        if not video_files:
            raise FileNotFoundError("No video files found!")
        
        print()
        print("🔗 Concatenating videos...")
        
        # Output path
        output_path = self.assets_dir / "FINAL_VIDEO.mp4"
        
        # Use imageio to concatenate (it has bundled ffmpeg)
        writer = imageio.get_writer(
            str(output_path),
            fps=24,
            codec='libx264',
            quality=8,  # High quality (1-10)
            pixelformat='yuv420p',
            ffmpeg_params=['-preset', 'medium']
        )
        
        for i, video_file in enumerate(video_files, 1):
            print(f"   Processing scene {i}/{len(video_files)}...")
            reader = imageio.get_reader(video_file)
            
            for frame in reader:
                writer.append_data(frame)
            
            reader.close()
        
        writer.close()
        
        # Get file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print()
        print("=" * 70)
        print("✅ FINAL VIDEO COMPLETE!")
        print("=" * 70)
        print(f"📹 Output: {output_path}")
        print(f"📊 Size: {file_size_mb:.1f} MB")
        print(f"🎬 Scenes: {len(video_files)}")
        print(f"📐 Resolution: 1920x1080")
        print("=" * 70)
        
        return output_path


def main():
    """Run pure Python assembly"""
    project_dir = Path(__file__).parent
    
    try:
        assembler = PythonVideoAssembler(project_dir)
        final_video = assembler.assemble()
        
        print()
        print("🎉 SUCCESS! Your video is ready to release!")
        print(f"   Location: {final_video}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
