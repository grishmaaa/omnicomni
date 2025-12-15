"""
TikTok Optimization Utilities

Converts videos to TikTok-optimized format:
- 9:16 vertical aspect ratio
- Auto-generated captions
- Hook optimization (first 3 seconds)
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import resize, crop

logger = logging.getLogger(__name__)


class TikTokOptimizer:
    """
    Optimize videos for TikTok
    
    Features:
    - Convert to 9:16 vertical
    - Add auto-captions
    - Optimize hook (first 3s)
    """
    
    # TikTok specs
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    TARGET_ASPECT = 9 / 16
    
    def __init__(self):
        logger.info("Initialized TikTokOptimizer")
    
    def optimize_video(
        self,
        input_path: Path,
        output_path: Path,
        add_captions: bool = True,
        caption_text: Optional[str] = None
    ) -> Path:
        """
        Optimize video for TikTok
        
        Args:
            input_path: Input video path
            output_path: Output video path
            add_captions: Whether to add captions
            caption_text: Caption text (auto-generated if None)
            
        Returns:
            Path to optimized video
        """
        logger.info(f"Optimizing video for TikTok: {input_path.name}")
        
        try:
            # Load video
            video = VideoFileClip(str(input_path))
            
            # Convert to 9:16
            video = self._convert_to_vertical(video)
            
            # Add captions if requested
            if add_captions:
                if caption_text is None:
                    caption_text = self._generate_caption(input_path)
                video = self._add_captions(video, caption_text)
            
            # Write output
            video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,  # TikTok prefers 30fps
                preset="medium",
                bitrate="8000k"  # High quality for TikTok
            )
            
            video.close()
            
            logger.info(f"✅ TikTok video saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TikTok optimization failed: {e}")
            raise RuntimeError(f"Failed to optimize for TikTok: {e}")
    
    def _convert_to_vertical(self, video: VideoFileClip) -> VideoFileClip:
        """Convert video to 9:16 vertical format"""
        width, height = video.size
        current_aspect = width / height
        
        if current_aspect > self.TARGET_ASPECT:
            # Video is too wide - crop sides
            new_width = int(height * self.TARGET_ASPECT)
            x_center = width / 2
            x1 = int(x_center - new_width / 2)
            video = crop(video, x1=x1, width=new_width)
        else:
            # Video is too tall - crop top/bottom
            new_height = int(width / self.TARGET_ASPECT)
            y_center = height / 2
            y1 = int(y_center - new_height / 2)
            video = crop(video, y1=y1, height=new_height)
        
        # Resize to TikTok dimensions
        video = resize(video, (self.TARGET_WIDTH, self.TARGET_HEIGHT))
        
        return video
    
    def _add_captions(
        self,
        video: VideoFileClip,
        text: str,
        position: str = "bottom"
    ) -> VideoFileClip:
        """Add text captions to video"""
        # Create text clip
        txt_clip = TextClip(
            text,
            fontsize=60,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(self.TARGET_WIDTH - 100, None)  # Leave margin
        )
        
        # Set duration to match video
        txt_clip = txt_clip.set_duration(video.duration)
        
        # Position caption
        if position == "bottom":
            txt_clip = txt_clip.set_position(('center', self.TARGET_HEIGHT - 300))
        elif position == "top":
            txt_clip = txt_clip.set_position(('center', 100))
        else:
            txt_clip = txt_clip.set_position('center')
        
        # Composite video with caption
        video = CompositeVideoClip([video, txt_clip])
        
        return video
    
    def _generate_caption(self, video_path: Path) -> str:
        """Generate caption from video filename"""
        # Simple caption based on filename
        name = video_path.stem.replace('_', ' ').title()
        return f"🎬 {name}"
    
    def optimize_hook(
        self,
        video_path: Path,
        output_path: Path,
        hook_duration: float = 3.0
    ) -> Path:
        """
        Extract and optimize the first 3 seconds (hook)
        
        Args:
            video_path: Input video
            output_path: Output hook video
            hook_duration: Hook duration in seconds
            
        Returns:
            Path to hook video
        """
        logger.info(f"Extracting {hook_duration}s hook from {video_path.name}")
        
        try:
            video = VideoFileClip(str(video_path))
            
            # Extract first N seconds
            hook = video.subclip(0, min(hook_duration, video.duration))
            
            # Add "Watch till the end!" caption
            hook = self._add_captions(hook, "👀 Watch till the end!", position="top")
            
            # Write hook
            hook.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                preset="fast"
            )
            
            video.close()
            hook.close()
            
            logger.info(f"✅ Hook saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Hook extraction failed: {e}")
            raise RuntimeError(f"Failed to create hook: {e}")


# Example usage
if __name__ == "__main__":
    optimizer = TikTokOptimizer()
    
    # Optimize a video for TikTok
    optimizer.optimize_video(
        input_path=Path("input.mp4"),
        output_path=Path("tiktok_ready.mp4"),
        add_captions=True,
        caption_text="🔥 Amazing AI Video!"
    )
    
    # Extract hook
    optimizer.optimize_hook(
        video_path=Path("input.mp4"),
        output_path=Path("hook.mp4"),
        hook_duration=3.0
    )
