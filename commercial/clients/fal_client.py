"""
Fal.ai API Client for Images and Video

Handles:
- FLUX.1-dev for photorealistic images
- Minimax Video-01 for image-to-video animation
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, List
import requests
import fal_client
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ImageResult(BaseModel):
    """Result from image generation"""
    url: str
    width: int
    height: int
    content_type: str = "image/png"


class VideoResult(BaseModel):
    """Result from video generation"""
    url: str
    duration: float
    width: int
    height: int


class FalClient:
    """
    Fal.ai API client for FLUX and Minimax
    
    Features:
    - FLUX.1-dev: Photorealistic image generation
    - Minimax Video-01: High-quality image-to-video
    - Cost tracking and retry logic
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Fal.ai client
        
        Args:
            api_key: Fal.ai API key
        """
        fal_client.api_key = api_key
        self.total_cost = 0.0
        
        logger.info("Initialized Fal.ai client")
    
    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        seed: Optional[int] = None
    ) -> ImageResult:
        """
        Generate image using FLUX.1-dev
        
        Args:
            prompt: Text description
            width: Image width (default 1024)
            height: Image height (default 1024)
            num_inference_steps: Quality steps (default 28)
            guidance_scale: Prompt adherence (default 3.5)
            seed: Random seed for reproducibility
            
        Returns:
            ImageResult with URL and metadata
            
        Raises:
            RuntimeError: If generation fails
        """
        logger.info(f"Generating image: {prompt[:60]}...")
        
        try:
            arguments = {
                "prompt": prompt,
                "image_size": {
                    "width": width,
                    "height": height
                },
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "num_images": 1,
                "enable_safety_checker": False
            }
            
            if seed is not None:
                arguments["seed"] = seed
            
            # Call Fal.ai API
            result = fal_client.subscribe(
                "fal-ai/flux-pro",
                arguments=arguments
            )
            
            # Extract result
            image_data = result["images"][0]
            
            # Track cost (~$0.03 per image)
            self.total_cost += 0.03
            
            logger.info(f"✅ Image generated: {image_data['url']}")
            
            return ImageResult(
                url=image_data["url"],
                width=image_data["width"],
                height=image_data["height"]
            )
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise RuntimeError(f"FLUX generation failed: {e}")
    
    def generate_video(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        duration: float = 5.0
    ) -> VideoResult:
        """
        Generate video from image using Minimax Video-01
        
        Args:
            image_url: URL of source image
            prompt: Optional text prompt for motion guidance
            duration: Video duration in seconds (default 5.0)
            
        Returns:
            VideoResult with URL and metadata
            
        Raises:
            RuntimeError: If generation fails
        """
        logger.info(f"Generating video from image: {image_url}")
        
        try:
            arguments = {
                "image_url": image_url,
                "prompt": prompt or "Cinematic camera movement, subtle motion"
            }
            
            # Call Fal.ai API
            result = fal_client.subscribe(
                "fal-ai/minimax-video",
                arguments=arguments
            )
            
            # Extract result
            video_data = result["video"]
            
            # Track cost (~$0.10 per 5s video)
            self.total_cost += 0.10
            
            logger.info(f"✅ Video generated: {video_data['url']}")
            
            return VideoResult(
                url=video_data["url"],
                duration=duration,
                width=video_data.get("width", 1024),
                height=video_data.get("height", 576)
            )
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise RuntimeError(f"Minimax generation failed: {e}")
    
    def download_file(self, url: str, output_path: Path) -> Path:
        """
        Download file from URL
        
        Args:
            url: File URL
            output_path: Local path to save
            
        Returns:
            Path to downloaded file
            
        Raises:
            RuntimeError: If download fails
        """
        try:
            logger.debug(f"Downloading: {url} -> {output_path}")
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ Downloaded: {output_path.name}")
            return output_path
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise RuntimeError(f"Failed to download {url}: {e}")
    
    def get_cost_estimate(self) -> float:
        """
        Get total cost estimate
        
        Returns:
            Total cost in USD
        """
        return self.total_cost
    
    def reset_usage(self):
        """Reset cost counter"""
        self.total_cost = 0.0
        logger.debug("Reset cost counter")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv(".env.commercial")
    
    client = FalClient(api_key=os.getenv("FAL_API_KEY"))
    
    # Generate image
    image = client.generate_image(
        prompt="Cyberpunk Tokyo street at night, neon signs, cinematic lighting, 35mm lens",
        width=1024,
        height=1024
    )
    print(f"\n🖼️  Image: {image.url}")
    
    # Generate video from image
    video = client.generate_video(
        image_url=image.url,
        prompt="Camera slowly pans right, neon lights flicker"
    )
    print(f"🎬 Video: {video.url}")
    
    print(f"\n💰 Total cost: ${client.get_cost_estimate():.2f}")
