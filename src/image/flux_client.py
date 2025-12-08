"""
Flux Image Generator
Wrapper for FLUX.1-schnell model via diffusers

Follows OmniComni architecture patterns:
- Integrates with src.core.config
- Uses existing logging patterns
- Compatible with pipeline_manager.py output
"""

import logging
from pathlib import Path
from typing import Optional
import torch
from diffusers import FluxPipeline


class FluxImageGenerator:
    """
    Production-grade Flux image generation
    
    Handles model loading, inference, and error recovery.
    Designed for server deployment with VRAM management.
    
    Example:
        >>> generator = FluxImageGenerator()
        >>> image_path = generator.generate(
        ...     prompt="Cyberpunk Tokyo street, 4k, neon lights",
        ...     output_path=Path("output/images/scene_01.png")
        ... )
    """
    
    def __init__(
        self,
        model_id: str = "black-forest-labs/FLUX.1-schnell",
        device: str = "cuda",
        dtype: torch.dtype = torch.bfloat16
    ):
        """
        Initialize Flux pipeline
        
        Args:
            model_id: HuggingFace model identifier
            device: Device to run on ("cuda" or "cpu")
            dtype: Model precision (bfloat16 or float16 for GPU)
            
        Technical decision: Using bfloat16 for stability on ampere+ GPUs
        """
        self.model_id = model_id
        self.device = device
        self.dtype = dtype
        self.pipeline = None
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing FluxImageGenerator with {model_id}")
        
        # Lazy loading - don't load until first generate() call
        # This allows multiple instances without VRAM issues
        self._load_model()
    
    def _load_model(self):
        """
        Load Flux pipeline with error handling
        
        Business reason: Model loading can fail due to VRAM, network, or auth issues.
        Graceful failure allows pipeline to continue with other scenes.
        """
        if self.pipeline is not None:
            self.logger.debug("Model already loaded, skipping")
            return
        
        try:
            self.logger.info(f"Loading Flux pipeline on {self.device}...")
            
            # Check device availability
            if self.device == "cuda" and not torch.cuda.is_available():
                self.logger.warning("CUDA requested but not available, falling back to CPU")
                self.device = "cpu"
                self.dtype = torch.float32
            
            # Load pipeline
            self.pipeline = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype
            ).to(self.device)
            
            # Enable memory optimizations if on GPU
            if self.device == "cuda":
                # Enable attention slicing to reduce VRAM
                self.pipeline.enable_attention_slicing()
                
                # Optional: VAE tiling for very large images
                # self.pipeline.enable_vae_tiling()
            
            vram = torch.cuda.memory_allocated() / 1e9 if self.device == "cuda" else 0
            self.logger.info(f"✅ Flux pipeline loaded ({vram:.2f}GB VRAM)")
            
        except torch.cuda.OutOfMemoryError:
            self.logger.error("❌ CUDA OOM: Insufficient VRAM for Flux model")
            self.logger.info("Suggestions: Close other GPU processes or use smaller batch size")
            raise
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load Flux pipeline: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        output_path: Path,
        seed: Optional[int] = None,
        num_inference_steps: int = 4,
        guidance_scale: float = 0.0,
        width: int = 1024,
        height: int = 1024
    ) -> Path:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of image
            output_path: Where to save generated image
            seed: Random seed for reproducibility
            num_inference_steps: Number of denoising steps (4 for Schnell)
            guidance_scale: CFG scale (0.0 for Schnell - it's distilled)
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Path to saved image
            
        Raises:
            RuntimeError: If generation fails
            
        Technical decision: Schnell uses 4 steps and no guidance (distilled model)
        """
        try:
            # Ensure model is loaded
            if self.pipeline is None:
                self._load_model()
            
            # Set seed for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
                self.logger.debug(f"Using seed: {seed}")
            
            self.logger.info(f"Generating image: {prompt[:50]}...")
            
            # Generate image
            result = self.pipeline(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height,
                generator=generator
            )
            
            # Extract image
            image = result.images[0]
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            image.save(output_path)
            self.logger.info(f"✅ Saved image: {output_path}")
            
            return output_path
            
        except torch.cuda.OutOfMemoryError:
            self.logger.error(f"❌ CUDA OOM while generating: {prompt[:50]}")
            self.logger.info("Suggestion: Reduce image size or clear VRAM")
            raise RuntimeError("CUDA Out of Memory")
            
        except Exception as e:
            self.logger.error(f"❌ Image generation failed: {e}")
            raise RuntimeError(f"Failed to generate image: {e}")
    
    def unload(self):
        """
        Free VRAM by unloading model
        
        Useful for batch processing where model isn't needed between batches
        """
        if self.pipeline is not None:
            self.logger.info("Unloading Flux pipeline to free VRAM")
            del self.pipeline
            self.pipeline = None
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
                self.logger.debug("VRAM cache cleared")
