"""
Flux.1 Image Generator (2025 State-of-the-Art)
Uses Flux.1-schnell for photorealistic quality

Replaces legacy SD 1.5 implementation
"""

import logging
from pathlib import Path
from typing import Optional
import torch
from diffusers import FluxPipeline

# Default model from config
DEFAULT_MODEL_ID = "black-forest-labs/FLUX.1-schnell"

class FluxImageGenerator:
    """
    Flux.1-schnell generator (2025 Standard)
    
    Why Flux?
    - Native 1024x1024 resolution
    - Incredible prompt adherence
    - Photorealistic lighting and textures
    - Fast inference (4 steps)
    """
    
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: str = "cuda",
        dtype: torch.dtype = torch.bfloat16
    ):
        """
        Initialize Flux pipeline
        
        Args:
            model_id: HuggingFace model
            device: Device ("cuda" or "cpu")
            dtype: Precision (bfloat16 recommended for Flux)
        """
        self.model_id = model_id
        self.device = device
        self.dtype = dtype
        self.pipeline = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing Flux with {model_id}")
        
        self._load_model()
    
    def _load_model(self):
        """Load Flux pipeline"""
        if self.pipeline is not None:
            return
        
        try:
            self.logger.info(f"Loading Flux pipeline (this may take a moment)...")
            
            # Check device
            if self.device == "cuda" and not torch.cuda.is_available():
                self.logger.warning("CUDA not available, utilizing CPU (Very Slow)")
                self.device = "cpu"
                self.dtype = torch.float32
            
            # Load pipeline
            self.pipeline = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype
            )
            
            # Memory optimizations
            if self.device == "cuda":
                # Offload for 24GB VRAM support
                self.pipeline.enable_model_cpu_offload()
            
            self.logger.info(f"✅ Flux loaded and ready")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load Flux: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        seed: Optional[int] = None,
        num_inference_steps: int = 4,  # Flux-schnell needs only 4 steps
        guidance_scale: float = 0.0,   # Flux doesn't use CFG usually (or uses 3.5 internally)
        width: int = 1024,
        height: int = 1024
    ) -> Path:
        """
        Generate image from prompt
        
        Args:
            prompt: Text description
            output_path: Where to save
            seed: Random seed
            num_inference_steps: Denoising steps (4 for Schnell, 20 for Dev)
            width: Image width (1024 default)
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
                generator = torch.Generator("cpu").manual_seed(seed)
            
            self.logger.info(f"Generating (Flux-Schnell): {prompt[:60]}...")
            
            # Generate
            result = self.pipeline(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale, # Unused for Schnell typically
                width=width,
                height=height,
                generator=generator,
                max_sequence_length=256 # Optimize for speed
            )
            
            image = result.images[0]
            
            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            self.logger.info(f"✅ Saved: {output_path.name}")
            return output_path
            
        except torch.cuda.OutOfMemoryError:
            self.logger.error("❌ CUDA OOM - Flux needs ~16GB VRAM. Ensure no other models are loaded.")
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


# Usage Alias
SDImageGenerator = FluxImageGenerator

