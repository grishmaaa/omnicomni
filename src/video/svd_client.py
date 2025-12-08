"""
Stable Video Diffusion Client
Image-to-Video generation using SVD-XT

Optimized for limited VRAM (8-12GB GPUs, T4 instances).
Follows OmniComni architecture patterns.
"""

import logging
from pathlib import Path
from typing import Optional
import torch
from PIL import Image
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
import gc


# Custom exception from our codebase
class VideoGenerationError(Exception):
    """Raised when video generation fails"""
    pass


class VideoGenerator:
    """
    Production-grade SVD video generation
    
    Optimizations for limited VRAM:
    - float16 precision (50% memory reduction)
    - CPU offloading (mandatory for <24GB VRAM)
    - VAE slicing (reduces decode memory)
    - Frame chunking (prevents OOM at end)
    
    Example:
        >>> generator = VideoGenerator()
        >>> video_path = generator.generate_clip(
        ...     image_path=Path("scene_01.png"),
        ...     output_path=Path("scene_01.mp4")
        ... )
    """
    
    # SVD native resolution (must match to avoid artifacts)
    NATIVE_WIDTH = 1024
    NATIVE_HEIGHT = 576
    
    # Generation defaults
    DEFAULT_FRAMES = 25  # ~4 seconds at 6 FPS
    DEFAULT_FPS = 6
    
    def __init__(
        self,
        model_id: str = "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
        device: str = "cuda"
    ):
        """
        Initialize SVD pipeline with aggressive VRAM optimizations
        
        Args:
            model_id: HuggingFace model ID
            device: Device ("cuda" or "cpu")
            
        Technical decisions:
        - float16: Halves VRAM usage with minimal quality loss
        - CPU offload: Moves inactive layers to CPU, critical for <24GB
        - VAE slicing: Splits VAE decode into chunks
        """
        self.model_id = model_id
        self.device = device
        self.pipeline = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing SVD VideoGenerator with {model_id}")
        
        self._load_model()
    
    def _load_model(self):
        """
        Load SVD pipeline with maximum VRAM efficiency
        
        Memory breakdown (for 12GB GPU):
        - Model weights: ~7GB (float16)
        - Activation memory: ~3-4GB
        - Output buffers: ~1-2GB
        Total: ~11-13GB without optimizations
        
        With optimizations: ~8-10GB (fits on 12GB GPU)
        """
        if self.pipeline is not None:
            self.logger.debug("Pipeline already loaded")
            return
        
        try:
            # Check device
            if self.device == "cuda" and not torch.cuda.is_available():
                self.logger.warning("CUDA not available, using CPU (SLOW!)")
                self.device = "cpu"
            
            self.logger.info(f"Loading SVD pipeline (~7GB download)...")
            
            # Load with float16 (50% memory savings)
            self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                variant="fp16"
            )
            
            # CRITICAL: Enable CPU offloading
            # Moves inactive model layers to CPU, freeing VRAM
            if self.device == "cuda":
                self.logger.info("Enabling CPU offloading (mandatory for <24GB VRAM)")
                self.pipeline.enable_model_cpu_offload()
            else:
                self.pipeline.to(self.device)
            
            # Note: SVD doesn't support enable_vae_slicing()
            # VAE memory is managed via decode_chunk_size parameter in generate()
            
            vram = torch.cuda.memory_allocated() / 1e9 if self.device == "cuda" else 0
            self.logger.info(f"✅ SVD pipeline loaded ({vram:.2f}GB VRAM)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load SVD pipeline: {e}")
            raise VideoGenerationError(f"Pipeline loading failed: {e}")
    
    def _prepare_image(self, image_path: Path) -> Image.Image:
        """
        Load and resize image to SVD native resolution
        
        Args:
            image_path: Path to input image
            
        Returns:
            Resized PIL Image
            
        Technical reason: SVD is trained on 1024x576. Other resolutions
        cause artifacts or generation failures.
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            original_size = image.size
            
            # Resize to SVD native resolution
            image = image.resize(
                (self.NATIVE_WIDTH, self.NATIVE_HEIGHT),
                Image.Resampling.LANCZOS
            )
            
            self.logger.debug(
                f"Resized image: {original_size} → "
                f"{self.NATIVE_WIDTH}x{self.NATIVE_HEIGHT}"
            )
            
            return image
            
        except Exception as e:
            raise VideoGenerationError(f"Failed to prepare image: {e}")
    
    def generate_clip(
        self,
        image_path: Path,
        output_path: Path,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.1,
        num_frames: int = DEFAULT_FRAMES,
        fps: int = DEFAULT_FPS,
        seed: Optional[int] = None
    ) -> Path:
        """
        Generate video clip from static image
        
        Args:
            image_path: Input image path
            output_path: Output video path (.mp4)
            motion_bucket_id: Motion intensity (1-255, default 127)
            noise_aug_strength: Noise augmentation (0.0-1.0, default 0.1)
            num_frames: Number of frames to generate (default 25)
            fps: Output video FPS (default 6)
            seed: Random seed for reproducibility
            
        Returns:
            Path to generated video
            
        Raises:
            VideoGenerationError: If generation fails
            
        Technical notes:
        - motion_bucket_id: Higher = more motion (127 is balanced)
        - noise_aug_strength: Higher = more variation from source
        - 25 frames @ 6 FPS = ~4 second clip
        """
        try:
            # Ensure pipeline loaded
            if self.pipeline is None:
                self._load_model()
            
            # Prepare image
            self.logger.info(f"Preparing image: {image_path.name}")
            image = self._prepare_image(image_path)
            
            # Set seed
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
                self.logger.debug(f"Using seed: {seed}")
            
            # Log generation params
            self.logger.info(
                f"Generating {num_frames} frames "
                f"(motion={motion_bucket_id}, noise={noise_aug_strength})"
            )
            
            # Generate frames
            # NOTE: This is the memory-intensive step
            frames = self.pipeline(
                image,
                decode_chunk_size=8,  # Chunk frames during decode (OOM prevention)
                num_frames=num_frames,
                motion_bucket_id=motion_bucket_id,
                noise_aug_strength=noise_aug_strength,
                generator=generator
            ).frames[0]
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export to MP4
            self.logger.info(f"Exporting video ({fps} FPS): {output_path.name}")
            export_to_video(frames, str(output_path), fps=fps)
            
            self.logger.info(f"✅ Video saved: {output_path}")
            return output_path
            
        except torch.cuda.OutOfMemoryError as e:
            # Attempt recovery
            self.logger.error("❌ CUDA OOM during video generation")
            self.logger.info("Attempting cleanup and retry...")
            
            # Cleanup
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Re-raise with context
            raise VideoGenerationError(
                f"Out of memory generating video. "
                f"Try: reduce num_frames or use smaller images"
            ) from e
            
        except Exception as e:
            self.logger.error(f"❌ Video generation failed: {e}")
            raise VideoGenerationError(f"Generation failed: {e}") from e
    
    def unload(self):
        """
        Free VRAM by unloading pipeline
        
        Use between batches to prevent memory buildup
        """
        if self.pipeline is not None:
            self.logger.info("Unloading SVD pipeline")
            del self.pipeline
            self.pipeline = None
            
            gc.collect()
            if self.device == "cuda":
                torch.cuda.empty_cache()
                self.logger.debug("VRAM cache cleared")
