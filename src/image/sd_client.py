"""
Stable Diffusion Image Generator (Lightweight Alternative)
Uses SD 1.5 (~4GB) instead of Flux (~23GB)

Drop-in replacement for FluxImageGenerator
"""

import logging
from pathlib import Path
from typing import Optional
import torch
from diffusers import StableDiffusionPipeline


class SDImageGenerator:
    """
    Stable Diffusion 1.5 generator
    
    Lightweight alternative to Flux (4GB vs 23GB)
    Perfect for disk-constrained environments
    
    Example:
        >>> generator = SDImageGenerator()
        >>> image_path = generator.generate(
        ...     prompt="Cyberpunk Tokyo street, neon lights",
        ...     output_path=Path("scene_01.png")
        ... )
    """
    
    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "cuda",
        dtype: torch.dtype = torch.float16
    ):
        """
        Initialize SD pipeline
        
        Args:
            model_id: HuggingFace model (SD 1.5 by default)
            device: Device ("cuda" or "cpu")
            dtype: Precision (float16 recommended for GPU)
        """
        self.model_id = model_id
        self.device = device
        self.dtype = dtype
        self.pipeline = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing SD with {model_id}")
        
        self._load_model()
    
    def _load_model(self):
        """Load SD pipeline"""
        if self.pipeline is not None:
            return
        
        try:
            self.logger.info(f"Loading SD pipeline (~4GB download)...")
            
            # Check device
            if self.device == "cuda" and not torch.cuda.is_available():
                self.logger.warning("CUDA not available, using CPU")
                self.device = "cpu"
                self.dtype = torch.float32
            
            # Load pipeline
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype,
                safety_checker=None,  # Disable for speed
                requires_safety_checker=False
            ).to(self.device)
            
            # Optimizations
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()
            
            vram = torch.cuda.memory_allocated() / 1e9 if self.device == "cuda" else 0
            self.logger.info(f"✅ SD loaded ({vram:.2f}GB VRAM)")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load SD: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        seed: Optional[int] = None,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        width: int = 512,
        height: int = 512
    ) -> Path:
        """
        Generate image from prompt
        
        Args:
            prompt: Text description
            output_path: Where to save
            seed: Random seed
            num_inference_steps: Denoising steps (20-50 typical)
            guidance_scale: CFG scale (7.5 default)
            width: Image width (512 default for SD 1.5)
            height: Image height
            
        Returns:
            Path to saved image
        """
        try:
            if self.pipeline is None:
                self._load_model()
            
            # Set seed
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            self.logger.info(f"Generating: {prompt[:60]}...")
            
            # Generate
            result = self.pipeline(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=generator
            )
            
            image = result.images[0]
            
            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            self.logger.info(f"✅ Saved: {output_path.name}")
            return output_path
            
        except torch.cuda.OutOfMemoryError:
            self.logger.error("❌ CUDA OOM - try reducing image size")
            raise
        except Exception as e:
            self.logger.error(f"❌ Generation failed: {e}")
            raise
    
    def unload(self):
        """Free VRAM"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            if self.device == "cuda":
                torch.cuda.empty_cache()


# Alias for compatibility
FluxImageGenerator = SDImageGenerator
