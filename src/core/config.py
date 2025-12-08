"""
Configuration Management using Pydantic Settings

Loads from .env file, no hardcoded secrets.
Environment variables override defaults.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration
    
    Supports .env file and environment variable overrides.
    
    Example .env:
        MODEL_ID=meta-llama/Llama-3.2-3B-Instruct
        VOICE_ID=en-US-ChristopherNeural
        TEMPERATURE=0.7
        HF_TOKEN=hf_xxxxx
    """
    
    # Model Configuration
    model_id: str = "meta-llama/Llama-3.2-3B-Instruct"
    use_4bit_quantization: bool = True
    temperature: float = 0.7
    max_new_tokens: int = 2000
    max_retries: int = 3
    
    # Voice Configuration
    voice_id: str = "en-US-ChristopherNeural"
    
    # API Keys (optional - from .env)
    hf_token: Optional[str] = None  # HuggingFace token
    openai_api_key: Optional[str] = None  # For future OpenAI integration
    
    # Output Configuration
    output_root: Path = Path("output")
    log_level: str = "INFO"
    
    # GPU Configuration
    cuda_visible_devices: Optional[str] = None  # e.g., "0,1,2,3"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars
    )
    
    @property
    def is_cuda_available(self) -> bool:
        """Check if CUDA configuration is set"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False


# Singleton instance
settings = Settings()


# Example usage in other files:
# from src.core.config import settings
# model_id = settings.model_id
