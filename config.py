"""
Configuration settings for OmniComni Audio Scene Generator
"""

from pathlib import Path

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# AI Model for scene generation
DEFAULT_MODEL = "meta-llama/Llama-3.2-3B-Instruct"

# Alternative models (in order of preference)
ALTERNATIVE_MODELS = [
    "meta-llama/Llama-3.2-3B",
    "meta-llama/Llama-3.1-8B-Instruct",
    "microsoft/phi-2",
]

# Model settings
USE_4BIT_QUANTIZATION = True  # Save memory with 4-bit quantization
MODEL_DEVICE_MAP = "auto"     # Automatically distribute across GPUs

# Image/Video Models
IMAGE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"  # 2025 SOTA
VIDEO_MODEL_ID = "stabilityai/stable-video-diffusion-img2vid-xt-1-1"

# ============================================================================
# GENERATION CONFIGURATION  
# ============================================================================

# Scene generation settings
DEFAULT_NUM_SCENES = 5
MAX_NEW_TOKENS = 1200
TEMPERATURE = 0.7              # 0.0 = deterministic, 1.0 = creative
TOP_P = 0.9
REPETITION_PENALTY = 1.1

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================

# Voice settings (edge-tts)
VOICE_MAP = {
    "neutral": "en-US-ChristopherNeural",
    "excited": "en-US-JennyNeural",
    "serious": "en-GB-RyanNeural",
    "mysterious": "en-US-GuyNeural",
    "dramatic": "en-US-AriaNeural",
}

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Output directories
OUTPUT_DIR = Path("output")
TEMP_DIR = Path(".temp")

# File naming
USE_TIMESTAMPS = True
MAX_FILENAME_LENGTH = 50

# ============================================================================
# LOGGING
# ============================================================================

VERBOSE = False                # Show debug information
SHOW_GENERATED_TEXT = False    # Show raw AI output (debug)

# ============================================================================
# PARALLEL PROCESSING
# ============================================================================

# Multi-GPU settings
ENABLE_MULTI_GPU = True        # Use multiple GPUs if available
MAX_PARALLEL_JOBS = 4          # Maximum concurrent generations
