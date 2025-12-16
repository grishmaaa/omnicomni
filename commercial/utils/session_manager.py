"""
Session Management Utilities

Handles temporary asset cleanup, video archival, thumbnail generation,
and video duration extraction for the AI video generator.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import cv2


def clear_temp_assets():
    """
    Clear all temporary assets from the assets directory
    
    Deletes all files in:
    - assets/images/
    - assets/videos/
    - assets/audio/
    
    This should be called before starting a new video generation
    to ensure no old files interfere with the new generation.
    """
    base_path = Path(__file__).parent.parent / "assets"
    
    subdirs = ["images", "videos", "audio"]
    
    for subdir in subdirs:
        dir_path = base_path / subdir
        
        if dir_path.exists():
            # Delete all files in directory
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete {file_path}: {e}")
    
    print("✅ Temporary assets cleared")


def archive_video(
    firebase_uid: str,
    topic: str,
    video_path: Path
) -> tuple[Path, Path]:
    """
    Archive completed video to user's permanent storage
    
    Args:
        firebase_uid: User's Firebase UID
        topic: Video topic (for folder naming)
        video_path: Path to the generated video file
        
    Returns:
        tuple: (archived_video_path, thumbnail_path)
    """
    # Create timestamp for folder name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create user's archive directory
    base_path = Path(__file__).parent.parent / "user_videos"
    user_dir = base_path / firebase_uid / timestamp
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy video to archive
    archived_video = user_dir / "FINAL_VIDEO.mp4"
    shutil.copy2(video_path, archived_video)
    
    # Generate thumbnail
    thumbnail_path = generate_thumbnail(archived_video)
    
    print(f"✅ Video archived to: {archived_video}")
    
    return archived_video, thumbnail_path


def generate_thumbnail(video_path: Path) -> Path:
    """
    Generate thumbnail from video's first frame
    
    Args:
        video_path: Path to video file
        
    Returns:
        Path: Path to generated thumbnail
    """
    thumbnail_path = video_path.parent / "thumbnail.png"
    
    try:
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        # Read first frame
        ret, frame = cap.read()
        
        if ret:
            # Resize to thumbnail size (320x180 for 16:9)
            thumbnail = cv2.resize(frame, (320, 180))
            
            # Save thumbnail
            cv2.imwrite(str(thumbnail_path), thumbnail)
            print(f"✅ Thumbnail generated: {thumbnail_path}")
        else:
            print("⚠️ Could not read video frame for thumbnail")
            thumbnail_path = None
        
        cap.release()
        
    except Exception as e:
        print(f"⚠️ Thumbnail generation failed: {e}")
        thumbnail_path = None
    
    return thumbnail_path


def get_video_duration(video_path: Path) -> int:
    """
    Get video duration in seconds
    
    Args:
        video_path: Path to video file
        
    Returns:
        int: Duration in seconds
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        
        # Get frame count and FPS
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        cap.release()
        
        if fps > 0:
            duration = int(frame_count / fps)
            return duration
        else:
            return 0
            
    except Exception as e:
        print(f"⚠️ Could not get video duration: {e}")
        return 0


def get_user_video_count(firebase_uid: str) -> int:
    """
    Get count of videos for a user
    
    Args:
        firebase_uid: User's Firebase UID
        
    Returns:
        int: Number of videos
    """
    base_path = Path(__file__).parent.parent / "user_videos"
    user_dir = base_path / firebase_uid
    
    if not user_dir.exists():
        return 0
    
    # Count subdirectories (each is a video)
    count = sum(1 for item in user_dir.iterdir() if item.is_dir())
    return count


# Example usage
if __name__ == "__main__":
    # Test clearing temp assets
    print("Testing clear_temp_assets()...")
    clear_temp_assets()
    
    # Test video archival (requires existing video)
    # video_path = Path("assets/FINAL_VIDEO.mp4")
    # if video_path.exists():
    #     archived, thumbnail = archive_video(
    #         "test_user_123",
    #         "Test Video",
    #         video_path
    #     )
    #     print(f"Archived: {archived}")
    #     print(f"Thumbnail: {thumbnail}")
