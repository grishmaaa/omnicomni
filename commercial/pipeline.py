"""
Commercial Video Generation Pipeline

Orchestrates the complete workflow:
1. Story generation (Groq)
2. Image generation (Fal.ai FLUX)
3. Video generation (Fal.ai Minimax)
4. Voice synthesis (ElevenLabs)
5. Final assembly (MoviePy)
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
import time
import gc

from commercial.clients.openai_client import OpenAIClient, StoryResponse
from .clients.fal_client import FalClient
from .clients.elevenlabs_client import ElevenLabsClient
from .config import config

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Track generation progress"""
    stage: str
    current: int
    total: int
    message: str
    cost_so_far: float = 0.0


class CommercialPipeline:
    """
    Production-ready video generation pipeline
    
    Features:
    - Automatic retry on failures
    - Progress tracking
    - Cost monitoring
    - File management
    """
    
    def __init__(
        self,
        openai_api_key: str,
        fal_api_key: str,
        elevenlabs_api_key: str
    ):
        """
        Initialize pipeline with API clients
        
        Args:
            together_api_key: Together API key
            fal_api_key: Fal.ai API key
            elevenlabs_api_key: ElevenLabs API key
        """
        # Initialize API clients
        self.openai_client = OpenAIClient(
            api_key=openai_api_key,
            model=config.OPENAI_MODEL
        )
        self.fal = FalClient(fal_api_key)
        self.elevenlabs = ElevenLabsClient(elevenlabs_api_key, config.ELEVENLABS_VOICE)
        
        self.progress_callback = None
        
        logger.info("Initialized CommercialPipeline")
    
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, stage: str, current: int, total: int, message: str):
        """Update progress"""
        if self.progress_callback:
            progress = GenerationProgress(
                stage=stage,
                current=current,
                total=total,
                message=message,
                cost_so_far=self.get_total_cost()
            )
            self.progress_callback(progress)
    
    def generate_video(
        self,
        topic: str,
        style: str = "cinematic",
        voice: Optional[str] = None,
        aspect_ratio: str = "16:9",
        output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Generate complete video from topic
        
        Args:
            topic: Video topic/theme
            style: Visual style (cinematic, anime, photorealistic)
            voice: Voice ID or preset
            aspect_ratio: Video aspect ratio (16:9 or 9:16)
            output_dir: Output directory (uses config default if None)
            
        Returns:
            Dictionary with file paths and metadata
        """
        start_time = time.time()
        
        if output_dir is None:
            output_dir = config.OUTPUT_DIR / self._sanitize_filename(topic)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting generation for topic: '{topic}'")
        
        try:
            # Stage 1: Generate story
            self._update_progress("story", 0, 5, "Generating story with AI...")
            story = self.openai_client.generate_story(
                topic=topic,
                num_scenes=config.NUM_SCENES,
                style=style
            )
            logger.info(f"Story generated: {story.title}")
            
            # Stage 2: Generate images
            self._update_progress("images", 0, len(story.scenes), "Creating images...")
            image_paths = []
            
            for i, scene in enumerate(story.scenes, 1):
                self._update_progress("images", i, len(story.scenes), f"Generating image {i}/{len(story.scenes)}")
                
                # Build prompt from structured scene data
                prompt = self._build_image_prompt(scene, style)
                
                # Calculate dimensions based on aspect ratio
                width, height = self._get_dimensions(aspect_ratio)
                
                # Generate image
                image_result = self.fal.generate_image(
                    prompt=prompt,
                    width=width,
                    height=height,
                    num_inference_steps=config.FLUX_STEPS
                )
                
                # Download image
                image_path = output_dir / f"scene_{scene.scene_id:02d}_image.png"
                self.fal.download_file(image_result.url, image_path)
                image_paths.append(image_path)
            
            # Stage 3: Generate videos
            self._update_progress("videos", 0, len(story.scenes), "Animating scenes...")
            video_paths = []
            
            for i, (scene, image_path) in enumerate(zip(story.scenes, image_paths), 1):
                self._update_progress("videos", i, len(story.scenes), f"Animating scene {i}/{len(story.scenes)}")
                
                # Generate video from image
                video_result = self.fal.generate_video(
                    image_url=str(image_path),  # Fal.ai accepts local paths
                    prompt=scene.visual_action,
                    duration=scene.duration
                )
                
                # Download video
                video_path = output_dir / f"scene_{scene.scene_id:02d}_video.mp4"
                self.fal.download_file(video_result.url, video_path)
                video_paths.append(video_path)
            
            # Stage 4: Generate voiceovers
            self._update_progress("voice", 0, len(story.scenes), "Generating voiceovers...")
            audio_paths = self.elevenlabs.generate_batch(
                texts=[scene.narration for scene in story.scenes],
                output_dir=output_dir,
                voice=voice,
                prefix="narration"
            )
            
            # Stage 5: Assemble final video
            self._update_progress("assembly", 0, 1, "Assembling final video...")
            final_video = self._assemble_video(
                video_paths=video_paths,
                audio_paths=audio_paths,
                output_path=output_dir / "final_video.mp4"
            )
            
            # Calculate stats
            duration = time.time() - start_time
            total_cost = self.get_total_cost()
            
            result = {
                "success": True,
                "final_video": final_video,
                "story": story,
                "num_scenes": len(story.scenes),
                "duration_seconds": duration,
                "total_cost": total_cost,
                "output_dir": output_dir
            }
            
            logger.info(f"✅ Video generation complete in {duration:.1f}s (${total_cost:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise RuntimeError(f"Video generation failed: {e}")
    
    def _build_image_prompt(self, scene, style: str) -> str:
        """Build optimized image prompt from scene data"""
        # Reuse existing prompt builder logic
        from src.image.prompt_builder import build_flux_prompt, QualityLevel
        
        scene_dict = {
            "visual_subject": scene.visual_subject,
            "visual_action": scene.visual_action,
            "background_environment": scene.background_environment,
            "lighting": scene.lighting,
            "camera_shot": scene.camera_shot
        }
        
        prompts = build_flux_prompt(
            scene=scene_dict,
            global_style=style,
            quality=QualityLevel.HIGH
        )
        
        return prompts["positive"]
    
    def _get_dimensions(self, aspect_ratio: str) -> tuple:
        """Get image dimensions for aspect ratio"""
        if aspect_ratio == "9:16":  # TikTok vertical
            return (576, 1024)
        elif aspect_ratio == "16:9":  # YouTube horizontal
            return (1024, 576)
        else:
            return (1024, 1024)  # Square
    
    def _assemble_video(
        self,
        video_paths: List[Path],
        audio_paths: List[Path],
        output_path: Path
    ) -> Path:
        """
        Assemble final video with MoviePy
        
        Args:
            video_paths: List of video clip paths
            audio_paths: List of audio clip paths
            output_path: Output video path
            
        Returns:
            Path to final video
        """
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
        
        logger.info("Assembling final video with MoviePy...")
        gc.collect() # Free up memory before heavy operation
        
        try:
            # Log memory before starting
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    available_kb = int([x for x in meminfo.splitlines() if 'MemAvailable' in x][0].split()[1])
                    logger.info(f"💾 Memory check before assembly: {available_kb/1024:.2f} MB available")
            except:
                logger.info("Could not read memory stats (not on Linux?)")

            clips = []
            
            for video_path, audio_path in zip(video_paths, audio_paths):
                # Load video and audio
                video = VideoFileClip(str(video_path))
                audio = AudioFileClip(str(audio_path))
                
                # Set audio
                video = video.set_audio(audio)
                
                # Match video duration to audio
                if video.duration < audio.duration:
                    # Loop video to match audio
                    video = video.loop(duration=audio.duration)
                else:
                    # Trim video to match audio
                    video = video.subclip(0, audio.duration)
                
                clips.append(video)
            
            # Concatenate all clips
            final = concatenate_videoclips(clips, method="compose")
            
            # Write final video - Optimized for Low Memory (Railway)
            final.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="veryfast",  # Faster encoding, slightly larger file, less RAM
                threads=1,          # CRITICAL: Forces sequential processing to prevent OOM
                audio_bitrate="128k"
            )
            
            # Cleanup
            for clip in clips:
                clip.close()
            final.close()
            
            logger.info(f"✅ Final video saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise RuntimeError(f"Failed to assemble video: {e}")
    
    def _sanitize_filename(self, text: str) -> str:
        """Create safe filename from text"""
        import re
        safe = re.sub(r'[^\w\s-]', '', text)
        safe = re.sub(r'[\s]+', '_', safe)
        return safe[:50].strip('_').lower()
    
    def get_total_cost(self) -> float:
        """Get total cost across all services"""
        return (
            self.openai_client.get_cost_estimate() +
            self.fal.get_cost_estimate() +
            self.elevenlabs.get_cost_estimate()
        )
    
    def reset_usage(self):
        """Reset all usage counters"""
        self.openai_client.reset_usage()
        self.fal.reset_usage()
        self.elevenlabs.reset_usage()


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv(".env.commercial")
    
    pipeline = CommercialPipeline(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        fal_api_key=os.getenv("FAL_API_KEY"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")
    )
    
    # Progress callback
    def on_progress(progress: GenerationProgress):
        print(f"[{progress.stage}] {progress.current}/{progress.total} - {progress.message} (${progress.cost_so_far:.2f})")
    
    pipeline.set_progress_callback(on_progress)
    
    # Generate video
    result = pipeline.generate_video(
        topic="Cyberpunk Tokyo at night",
        style="cinematic",
        aspect_ratio="16:9"
    )
    
    print(f"\n✅ Success!")
    print(f"Video: {result['final_video']}")
    print(f"Cost: ${result['total_cost']:.2f}")
    print(f"Duration: {result['duration_seconds']:.1f}s")
