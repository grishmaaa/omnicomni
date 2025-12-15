"""
Commercial Pipeline Configuration

Environment variables for production API services.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class CommercialConfig(BaseSettings):
    """Configuration for commercial API pipeline"""
    
    # API Keys (optional - will show error in UI if not set)
    GROQ_API_KEY: str = Field(default="", description="Groq API key for LLM")
    FAL_API_KEY: str = Field(default="", description="Fal.ai API key for images/video")
    ELEVENLABS_API_KEY: str = Field(default="", description="ElevenLabs API key for voice")
    
    # Model Configuration
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    FLUX_MODEL: str = "fal-ai/flux-pro"
    MINIMAX_MODEL: str = "fal-ai/minimax-video"
    ELEVENLABS_VOICE: str = "Rachel"  # Default voice
    
    # Generation Settings
    NUM_SCENES: int = 5
    IMAGE_SIZE: int = 1024
    VIDEO_DURATION: int = 5  # seconds per scene
    FLUX_STEPS: int = 28
    
    # Cost Limits
    MAX_COST_PER_VIDEO: float = 2.00
    MONTHLY_BUDGET: float = 100.00
    
    # Output Settings
    OUTPUT_DIR: Path = Path("commercial/output")
    TEMP_DIR: Path = Path("commercial/.temp")
    
    # TikTok Settings
    TIKTOK_ASPECT_RATIO: str = "9:16"  # Vertical
    YOUTUBE_ASPECT_RATIO: str = "16:9"  # Horizontal
    DEFAULT_ASPECT_RATIO: str = "16:9"
    
    class Config:
        env_file = ".env.commercial"
        env_file_encoding = "utf-8"


# Global config instance
try:
    config = CommercialConfig()
except Exception as e:
    # If .env.commercial doesn't exist, create config with defaults
    import warnings
    warnings.warn(f"Could not load .env.commercial: {e}. Using default config.")
    config = CommercialConfig(_env_file=None)


# Ensure directories exist
config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
config.TEMP_DIR.mkdir(parents=True, exist_ok=True)

