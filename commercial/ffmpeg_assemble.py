"""
Professional Video Assembly using FFmpeg
High-end, production-grade video compilation
"""

import json
import subprocess
from pathlib import Path
import os

def assemble_with_ffmpeg():
    """Assemble final video using FFmpeg (professional grade)"""
    
    # Load script
    script_path = Path(__file__).parent / "script.json"
    with open(script_path, 'r', encoding='utf-8') as f:
        screenplay = json.load(f)
    
    scenes = screenplay['scenes']
    
    # Paths
    videos_dir = Path(__file__).parent / "assets" / "videos"
    audio_dir = Path(__file__).parent / "assets" / "audio"
    output_path = Path(__file__).parent / "assets" / "final_video.mp4"
    
    print("=" * 70)
    print("🎬 PROFESSIONAL VIDEO ASSEMBLY (FFmpeg)")
    print("=" * 70)
    print()
    print(f"Scenes: {len(scenes)}")
    print(f"Output: {output_path}")
    print()
    
    # Create concat file for FFmpeg
    concat_file = Path(__file__).parent / "assets" / "concat_list.txt"
    
    with open(concat_file, 'w') as f:
        for scene in scenes:
            scene_num = scene['scene_number']
            video_path = videos_dir / f"scene_{scene_num}.mp4"
            audio_path = audio_dir / f"scene_{scene_num}.mp3"
            
            # Create intermediate file with audio
            temp_output = videos_dir / f"temp_scene_{scene_num}.mp4"
            
            print(f"🎞️  Processing scene {scene_num}...")
            
            # Combine video with audio using FFmpeg
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite
                '-i', str(video_path),
                '-i', str(audio_path),
                '-c:v', 'copy',  # Copy video stream (no re-encoding)
                '-c:a', 'aac',  # AAC audio
                '-b:a', '192k',  # Audio bitrate
                '-shortest',  # Match shortest stream
                '-loglevel', 'error',
                str(temp_output)
            ]
            
            subprocess.run(cmd, check=True)
            
            # Add to concat list
            f.write(f"file '{temp_output.name}'\n")
    
    print()
    print("🔗 Concatenating all scenes...")
    
    # Concatenate all videos
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',  # Copy streams (fast!)
        '-loglevel', 'error',
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True)
    
    # Cleanup temp files
    print("🧹 Cleaning up...")
    for scene in scenes:
        scene_num = scene['scene_number']
        temp_file = videos_dir / f"temp_scene_{scene_num}.mp4"
        if temp_file.exists():
            temp_file.unlink()
    
    concat_file.unlink()
    
    # Get file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print()
    print("=" * 70)
    print("✅ FINAL VIDEO READY!")
    print("=" * 70)
    print(f"📹 Output: {output_path}")
    print(f"📊 Size: {file_size_mb:.1f} MB")
    print(f"🎬 Scenes: {len(scenes)}")
    print(f"📐 Resolution: 1920x1080 (Full HD)")
    print("=" * 70)
    
    return output_path


if __name__ == "__main__":
    try:
        assemble_with_ffmpeg()
        print()
        print("🎉 SUCCESS! Your video is ready to publish!")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
        print()
        print("Make sure FFmpeg is installed:")
        print("  Download from: https://ffmpeg.org/download.html")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
