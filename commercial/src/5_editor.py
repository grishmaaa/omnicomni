"""
Video Editor Module (5_editor.py)

Assembles final master video by synchronizing scenes with audio narration.
Implements professional post-production techniques with memory management.

Author: Senior Post-Production Engineer
Purpose: Final assembly module of AI Video Generator pipeline
"""

import json
import os
from pathlib import Path
import math
try:
    # MoviePy 2.x
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
except ImportError:
    # MoviePy 1.x (fallback)
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# ============================================================================
# Configuration & Constants
# ============================================================================

# Target resolution (all clips resized to this before concatenation)
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
TARGET_RESOLUTION = (TARGET_WIDTH, TARGET_HEIGHT)

# Export settings
OUTPUT_FPS = 24
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
PRESET = "medium"  # Options: ultrafast, fast, medium, slow, veryslow
THREADS = 4  # Multi-threading for faster rendering


def edit_video(script_path: str = "script.json", output_filename: str = "final_video.mp4") -> Path:
    """
    Assemble final master video from scenes.
    
    This function synchronizes video clips with audio narration, handles
    duration mismatches via looping/trimming, and renders a production-ready
    final video.
    
    Process Flow:
    1. Load scene order from screenplay
    2. For each scene:
       a. Load video and audio
       b. Synchronize durations (loop video if needed)
       c. Resize to target resolution
       d. Set audio track
    3. Concatenate all scenes
    4. Render final master video
    
    Features:
    - Audio-driven timing ("Audio is King")
    - Video looping for duration matching
    - Resolution standardization (prevents FFMPEG crashes)
    - Memory management (explicit cleanup)
    - Professional export settings
    
    Args:
        script_path: Path to screenplay JSON (default: "script.json")
        output_filename: Name of final video (default: "final_video.mp4")
        
    Returns:
        Path: Path to final rendered video
        
    Technical Details:
        - Resolution: 1920x1080 (standardized)
        - FPS: 24 (cinematic standard)
        - Video Codec: libx264 (universal compatibility)
        - Audio Codec: AAC (web/mobile compatible)
        - Method: compose (safer than chain)
    """
    
    # Load screenplay for scene order
    script_file = Path(__file__).parent.parent / script_path
    if not script_file.exists():
        raise FileNotFoundError(
            f"Screenplay not found: {script_file}\n"
            f"Run 1_script_gen.py first to generate the screenplay."
        )
    
    with open(script_file, 'r', encoding='utf-8') as f:
        screenplay = json.load(f)
    
    scenes = screenplay.get('scenes', [])
    if not scenes:
        raise ValueError("No scenes found in screenplay")
    
    # Ensure asset directories exist
    videos_dir = Path(__file__).parent.parent / "assets" / "videos"
    audio_dir = Path(__file__).parent.parent / "assets" / "audio"
    
    if not videos_dir.exists():
        raise FileNotFoundError(
            f"Videos directory not found: {videos_dir}\n"
            f"Run 3_video_gen.py first to generate videos."
        )
    
    if not audio_dir.exists():
        raise FileNotFoundError(
            f"Audio directory not found: {audio_dir}\n"
            f"Run 4_audio_gen.py first to generate audio."
        )
    
    # Output path
    output_dir = Path(__file__).parent.parent / "assets"
    output_path = output_dir / output_filename
    
    print("=" * 70)
    print("🎬 AI Video Generator - Final Assembly")
    print("=" * 70)
    print(f"\nTarget Resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}")
    print(f"FPS: {OUTPUT_FPS}")
    print(f"Codec: {VIDEO_CODEC} / {AUDIO_CODEC}")
    print()
    
    processed_clips = []
    total_scenes = len(scenes)
    
    try:
        # Process each scene
        for i, scene in enumerate(scenes, 1):
            scene_number = scene.get('scene_number', i)
            
            # File paths
            video_filename = f"scene_{scene_number}.mp4"
            audio_filename = f"scene_{scene_number}.mp3"
            
            video_path = videos_dir / video_filename
            audio_path = audio_dir / audio_filename
            
            # Check if files exist
            if not video_path.exists():
                print(f"⚠️  Scene {scene_number}/{total_scenes}: Video not found, skipping")
                print(f"   Missing: {video_path}")
                continue
            
            if not audio_path.exists():
                print(f"⚠️  Scene {scene_number}/{total_scenes}: Audio not found, skipping")
                print(f"   Missing: {audio_path}")
                continue
            
            print(f"🎞️  Scene {scene_number}/{total_scenes}: Processing...")
            
            # Load video and audio
            video_clip = VideoFileClip(str(video_path))
            audio_clip = AudioFileClip(str(audio_path))
            
            video_duration = video_clip.duration
            audio_duration = audio_clip.duration
            
            print(f"   Video duration: {video_duration:.2f}s")
            print(f"   Audio duration: {audio_duration:.2f}s")
            
            # ================================================================
            # SYNCHRONIZATION LOGIC ("Audio is King")
            # ================================================================
            # The audio narration determines the final scene duration.
            # We adjust the video to match the audio length.
            #
            # SCENARIO A: Audio > Video (Audio is longer)
            #   - Loop the video to fill the audio duration
            #   - Example: 3s video, 7s audio → loop video 3 times (9s), trim to 7s
            #   - Why loop? AI-generated video looks terrible when slowed down
            #
            # SCENARIO B: Video > Audio (Video is longer)
            #   - Trim the video to match audio duration
            #   - Example: 8s video, 5s audio → use first 5s of video
            #
            # SCENARIO C: Perfect match
            #   - Use as-is (rare, but possible)
            # ================================================================
            
            if audio_duration > video_duration:
                # SCENARIO A: Loop video to match audio
                # Calculate how many times to loop
                loops_needed = math.ceil(audio_duration / video_duration)
                
                print(f"   ⟳ Looping video {loops_needed}x to match audio")
                
                # Loop the video
                looped_video = video_clip.loop(n=loops_needed)
                
                # Trim to exact audio duration
                synced_video = looped_video.subclip(0, audio_duration)
                
            elif video_duration > audio_duration:
                # SCENARIO B: Trim video to match audio
                print(f"   ✂️  Trimming video to match audio")
                synced_video = video_clip.subclip(0, audio_duration)
                
            else:
                # SCENARIO C: Perfect match
                print(f"   ✅ Duration match (no adjustment needed)")
                synced_video = video_clip
            
            # ================================================================
            # RESOLUTION STANDARDIZATION
            # ================================================================
            # CRITICAL: All clips must have identical resolution before
            # concatenation. Even a 1-pixel difference will cause FFMPEG
            # to crash during final write.
            #
            # We resize all clips to TARGET_RESOLUTION (1920x1080)
            # ================================================================
            
            print(f"   📐 Resizing to {TARGET_WIDTH}x{TARGET_HEIGHT}")
            synced_video = synced_video.resize(newsize=TARGET_RESOLUTION)
            
            # Set audio track
            synced_video = synced_video.set_audio(audio_clip)
            
            # Add to processed clips list
            processed_clips.append(synced_video)
            
            print(f"   ✅ Scene {scene_number} processed")
            print()
        
        if not processed_clips:
            raise ValueError("No clips were successfully processed")
        
        # ================================================================
        # CONCATENATION & RENDERING
        # ================================================================
        
        print(f"🔗 Concatenating {len(processed_clips)} scenes...")
        print(f"   Method: compose (safer for format handling)")
        
        # Concatenate all clips
        # method="compose" is slower but handles format discrepancies better
        final_clip = concatenate_videoclips(processed_clips, method="compose")
        
        total_duration = final_clip.duration
        print(f"   Total duration: {total_duration:.2f}s ({total_duration/60:.1f} minutes)")
        
        # Render final video
        print()
        print(f"🎥 Rendering final video...")
        print(f"   Output: {output_path}")
        print(f"   This may take several minutes...")
        print()
        
        final_clip.write_videofile(
            str(output_path),
            fps=OUTPUT_FPS,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            preset=PRESET,
            threads=THREADS,
            verbose=False,  # Reduce console spam
            logger=None     # Disable progress bar for cleaner output
        )
        
        # ================================================================
        # RESOURCE CLEANUP
        # ================================================================
        # Explicitly close all clips to prevent memory leaks
        # MoviePy can leave temp files if not properly cleaned up
        # ================================================================
        
        print()
        print("🧹 Cleaning up resources...")
        
        for clip in processed_clips:
            clip.close()
        
        final_clip.close()
        
        # Get file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print()
        print("=" * 70)
        print("✅ Final video rendered successfully!")
        print(f"   Output: {output_path}")
        print(f"   Duration: {total_duration:.2f}s")
        print(f"   File size: {file_size_mb:.1f} MB")
        print(f"   Resolution: {TARGET_WIDTH}x{TARGET_HEIGHT}")
        print(f"   FPS: {OUTPUT_FPS}")
        print("=" * 70)
        
        return output_path
        
    except Exception as e:
        # Cleanup on error
        print(f"\n❌ Error during rendering: {e}")
        
        # Try to close any open clips
        for clip in processed_clips:
            try:
                clip.close()
            except:
                pass
        
        raise


# ============================================================================
# Looping Logic Explanation
# ============================================================================
"""
VIDEO LOOPING LOGIC - DETAILED EXPLANATION:

PROBLEM:
When audio narration is longer than the video clip, we need to extend
the video to match. We have two options:
1. Slow down the video (BAD - AI video artifacts look terrible in slow-mo)
2. Loop the video (GOOD - seamless repetition)

SOLUTION:
We use moviepy's .loop(n=X) method to repeat the video.

EXAMPLE SCENARIO:
- Video duration: 3.5 seconds
- Audio duration: 8.2 seconds
- Loops needed: ceil(8.2 / 3.5) = ceil(2.34) = 3 loops

STEP-BY-STEP:
1. Original video: [0s -------- 3.5s]
2. After loop(n=3): [0s -------- 3.5s][3.5s -------- 7.0s][7.0s -------- 10.5s]
3. After subclip(0, 8.2): [0s -------- 8.2s] (trimmed to exact audio length)

WHY CEIL?
We need AT LEAST enough loops to cover the audio duration.
- If we used floor(), we might not have enough video
- Example: 2 loops = 7.0s (not enough for 8.2s audio)
- With 3 loops = 10.5s (enough, then we trim to 8.2s)

VISUAL RESULT:
The video will play through completely, then restart and play again.
For AI-generated video, this is usually seamless because:
- AI video is often abstract/atmospheric
- Scenes are short (3-5s)
- Narration distracts from the loop point

DEBUGGING TIPS:
If the loop looks too repetitive:
1. Generate longer videos (increase duration in 3_video_gen.py)
2. Use shorter narration (edit script.json)
3. Add crossfade transitions (advanced - requires vfx.crossfadein)
"""


# ============================================================================
# Execution Block
# ============================================================================

if __name__ == "__main__":
    """
    Example usage: Assemble final video from scenes.
    
    Prerequisites:
        1. Run 1_script_gen.py to create script.json
        2. Run 2_image_gen.py to create images
        3. Run 3_video_gen.py to create videos
        4. Run 4_audio_gen.py to create audio
    
    To run this script:
        cd commercial/src
        python 5_editor.py
    
    Output:
        - Prints assembly progress to console
        - Saves final video to commercial/assets/final_video.mp4
        - Shows duration and file size
        
    Note:
        Rendering can take several minutes depending on:
        - Number of scenes
        - Total duration
        - CPU speed
        - Preset quality (medium = balanced)
    """
    
    print("=" * 70)
    print("🎬 AI Video Generator - Final Assembly Module")
    print("=" * 70)
    print()
    
    try:
        # Assemble final video
        output_path = edit_video()
        
        print()
        print("🎉 Pipeline complete!")
        print(f"   Your final video is ready: {output_path}")
        print()
        print("Next steps:")
        print("   1. Review the video")
        print("   2. Share on social media")
        print("   3. Generate more videos!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure to run all previous steps:")
        print("   1. python 1_script_gen.py")
        print("   2. python 2_image_gen.py")
        print("   3. python 3_video_gen.py")
        print("   4. python 4_audio_gen.py")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
