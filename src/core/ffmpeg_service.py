"""
FFmpeg Service
Robust wrapper for FFmpeg operations

Follows OmniComni patterns - validates environment before use.
Located in src/core (not src/services) to match our architecture.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional
import json


# Custom exception from our codebase
from src.core.exceptions import ConfigurationError


logger = logging.getLogger(__name__)


class FFmpegService:
    """
    Production-grade FFmpeg wrapper
    
    Validates FFmpeg binary availability on initialization.
    Provides high-level operations for video/audio processing.
    
    Example:
        >>> service = FFmpegService()  # Fails if FFmpeg not installed
        >>> metadata = service.get_video_metadata(Path("video.mp4"))
        >>> print(metadata['duration'])
    """
    
    def __init__(self):
        """
        Initialize FFmpeg service
        
        Validates that ffmpeg and ffprobe binaries are in PATH.
        
        Raises:
            ConfigurationError: If FFmpeg binaries not found
            
        Technical reason: Fail fast - better to crash on init than
        halfway through a batch processing job.
        """
        self.logger = logging.getLogger(__name__)
        
        # Check for ffmpeg binary
        self.ffmpeg_path = shutil.which("ffmpeg")
        if not self.ffmpeg_path:
            raise ConfigurationError(
                "FFmpeg binary not found in PATH.\n"
                "Installation:\n"
                "  Linux: sudo apt install ffmpeg\n"
                "  Windows: Download from https://github.com/BtbN/FFmpeg-Builds/releases\n"
                "           Extract and add to PATH\n"
                "  Verify: ffmpeg -version"
            )
        
        # Check for ffprobe binary (needed for metadata)
        self.ffprobe_path = shutil.which("ffprobe")
        if not self.ffprobe_path:
            raise ConfigurationError(
                "FFprobe binary not found in PATH.\n"
                "FFprobe comes with FFmpeg - please ensure full FFmpeg installation."
            )
        
        self.logger.info(f"✅ FFmpeg initialized: {self.ffmpeg_path}")
        self.logger.debug(f"FFprobe path: {self.ffprobe_path}")
    
    def get_video_metadata(self, file_path: Path) -> Dict:
        """
        Extract video metadata using ffprobe
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary with video metadata:
            - duration: Video length in seconds
            - width: Video width in pixels
            - height: Video height in pixels
            - codec_name: Video codec (e.g., h264)
            - fps: Frames per second
            
        Raises:
            FileNotFoundError: If video file doesn't exist
            RuntimeError: If ffprobe fails (corrupt video)
            
        Example:
            >>> metadata = service.get_video_metadata(Path("scene.mp4"))
            >>> print(f"{metadata['width']}x{metadata['height']}")
            1024x576
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")
        
        try:
            # Run ffprobe to get JSON metadata
            cmd = [
                self.ffprobe_path,
                "-v", "error",  # Only show errors
                "-select_streams", "v:0",  # First video stream
                "-show_entries", "stream=width,height,codec_name,r_frame_rate,duration",
                "-of", "json",  # Output as JSON
                str(file_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse JSON output
            data = json.loads(result.stdout)
            
            if not data.get("streams"):
                raise RuntimeError("No video streams found in file")
            
            stream = data["streams"][0]
            
            # Calculate FPS from fractional representation
            fps_str = stream.get("r_frame_rate", "0/1")
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 0
            
            # Get duration (may be in stream or format)
            duration = float(stream.get("duration", 0))
            
            metadata = {
                "width": int(stream.get("width", 0)),
                "height": int(stream.get("height", 0)),
                "codec_name": stream.get("codec_name", "unknown"),
                "fps": round(fps, 2),
                "duration": round(duration, 2)
            }
            
            self.logger.debug(f"Metadata for {file_path.name}: {metadata}")
            return metadata
            
            self.logger.debug(f"Metadata for {file_path.name}: {metadata}")
            return metadata
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFprobe failed: {e.stderr}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse ffprobe output: {e}")

    def get_probe_info(self, file_path: Path) -> Dict:
        """
        Get full probe info (all streams)
        
        Args:
            file_path: Path to media file
            
        Returns:
            Dictionary with 'streams' and 'format'
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "stream=index,codec_type,codec_name,channels,sample_rate,duration:format=duration,size",
            "-of", "json",
            str(file_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            raise RuntimeError(f"Probe failed: {e}")

    def has_audio_stream(self, file_path: Path) -> bool:
        """Check if file has an audio stream"""
        try:
            info = self.get_probe_info(file_path)
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    return True
            return False
        except:
            return False
    
    def extract_audio(
        self,
        input_path: Path,
        output_path: Path,
        audio_codec: str = "libmp3lame",
        audio_bitrate: str = "192k"
    ) -> Path:
        """
        Extract audio track from video
        
        Args:
            input_path: Input video file
            output_path: Output audio file (.mp3 or .wav)
            audio_codec: Audio codec (default: libmp3lame for MP3)
            audio_bitrate: Audio bitrate (default: 192k)
            
        Returns:
            Path to extracted audio file
            
        Raises:
            FileNotFoundError: If input video doesn't exist
            RuntimeError: If extraction fails
            
        Example:
            >>> service.extract_audio(
            ...     Path("video.mp4"),
            ...     Path("audio.mp3")
            ... )
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input video not found: {input_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.logger.info(f"Extracting audio: {input_path.name} → {output_path.name}")
            
            cmd = [
                self.ffmpeg_path,
                "-i", str(input_path),
                "-vn",  # No video
                "-acodec", audio_codec,
                "-ab", audio_bitrate,
                "-y",  # Overwrite output
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ Audio extracted: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio extraction failed: {e.stderr}")
    
    def merge_video_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        video_codec: str = "copy",
        audio_codec: str = "aac"
    ) -> Path:
        """
        Merge video and audio into single file
        
        Args:
            video_path: Input video (may have no audio)
            audio_path: Input audio (MP3, WAV, etc.)
            output_path: Output merged video
            video_codec: Video codec (default: copy - no re-encode)
            audio_codec: Audio codec (default: aac)
            
        Returns:
            Path to merged video
            
        Raises:
            FileNotFoundError: If inputs don't exist
            RuntimeError: If merge fails
            
        Example:
            >>> service.merge_video_audio(
            ...     Path("scene_01.mp4"),
            ...     Path("scene_01.mp3"),
            ...     Path("final_01.mp4")
            ... )
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.logger.info(f"Merging: {video_path.name} + {audio_path.name}")
            
            cmd = [
                self.ffmpeg_path,
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", video_codec,  # Copy video (no re-encode)
                "-c:a", audio_codec,  # Re-encode audio if needed
                "-shortest",  # Match shortest stream
                "-y",  # Overwrite
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ Merged video: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Video merge failed: {e.stderr}")
    
    def generate_test_video(
        self,
        output_path: Path,
        duration: int = 5,
        width: int = 640,
        height: int = 480
    ) -> Path:
        """
        Generate synthetic test video
        
        Useful for testing without needing actual video files.
        
        Args:
            output_path: Where to save test video
            duration: Video length in seconds
            width: Video width
            height: Video height
            
        Returns:
            Path to generated video
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.logger.info(f"Generating test video: {output_path.name}")
            
            cmd = [
                self.ffmpeg_path,
                "-f", "lavfi",
                "-i", f"testsrc=duration={duration}:size={width}x{height}:rate=30",
                "-f", "lavfi",
                "-i", "sine=frequency=1000:duration={}".format(duration),
                "-pix_fmt", "yuv420p",
                "-y",
                str(output_path)
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
            self.logger.info(f"✅ Test video generated: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Test video generation failed: {e.stderr}")
