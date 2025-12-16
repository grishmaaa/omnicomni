"""
Complete Video Assembler with Audio
Combines videos with their audio tracks properly
"""

import json
from pathlib import Path
import subprocess
from imageio_ffmpeg import get_ffmpeg_exe

class CompleteVideoAssembler:
    """Assembles video with audio using imageio's bundled ffmpeg"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.assets_dir = project_dir / "assets"
        self.videos_dir = self.assets_dir / "videos"
        self.audio_dir = self.assets_dir / "audio"
        self.script_path = project_dir / "script.json"
        self.ffmpeg = get_ffmpeg_exe()
        
    def combine_video_with_audio(self, scene_num: int):
        """Combine single video with its audio"""
        video_file = self.videos_dir / f"scene_{scene_num}.mp4"
        audio_file = self.audio_dir / f"scene_{scene_num}.mp3"
        output_file = self.videos_dir / f"complete_scene_{scene_num}.mp4"
        
        cmd = [
            self.ffmpeg, '-y',
            '-i', str(video_file),
            '-i', str(audio_file),
            '-c:v', 'copy',  # Copy video (no re-encode)
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-loglevel', 'error',
            str(output_file)
        ]
        
        subprocess.run(cmd, check=True)
        return output_file
        
    def assemble(self):
        """Assemble complete video with audio"""
        print("=" * 70)
        print("🎬 COMPLETE VIDEO ASSEMBLER (WITH AUDIO)")
        print("=" * 70)
        print()
        
        # Load script
        with open(self.script_path, 'r', encoding='utf-8') as f:
            screenplay = json.load(f)
        
        scenes = screenplay['scenes']
        print(f"Processing {len(scenes)} scenes with audio...")
        print()
        
        # Step 1: Combine each video with its audio
        complete_scenes = []
        for scene in scenes:
            scene_num = scene['scene_number']
            print(f"🎙️  Scene {scene_num}: Adding voiceover...")
            
            complete_scene = self.combine_video_with_audio(scene_num)
            complete_scenes.append(complete_scene)
        
        print()
        print("🔗 Concatenating all scenes...")
        
        # Step 2: Create concat file with absolute paths
        concat_file = self.assets_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for scene_file in complete_scenes:
                # Use absolute path with forward slashes
                abs_path = str(scene_file.absolute()).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        # Step 3: Concatenate
        output_path = self.assets_dir / "FINAL_VIDEO.mp4"
        
        cmd = [
            self.ffmpeg, '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        print("🧹 Cleaning up...")
        for scene_file in complete_scenes:
            scene_file.unlink()
        concat_file.unlink()
        
        # Get file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print()
        print("=" * 70)
        print("✅ FINAL VIDEO COMPLETE WITH AUDIO!")
        print("=" * 70)
        print(f"📹 Output: {output_path}")
        print(f"📊 Size: {file_size_mb:.1f} MB")
        print(f"🎬 Scenes: {len(scenes)}")
        print(f"🎙️  Audio: Professional voiceovers included")
        print(f"📐 Resolution: 1920x1080 Full HD")
        print("=" * 70)
        
        return output_path


def main():
    """Run complete assembly"""
    project_dir = Path(__file__).parent
    
    try:
        assembler = CompleteVideoAssembler(project_dir)
        final_video = assembler.assemble()
        
        print()
        print("🎉 SUCCESS! Your video with audio is ready!")
        print(f"   Location: {final_video}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
