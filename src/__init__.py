"""
OmniComni - AI Audio Scene Generation
Generates audio dramas from topics using AI scene generation and text-to-speech
"""

__version__ = "1.0.0"
__author__ = "OmniComni Team"

from .scene_generator import SceneGenerator
from .audio_generator import AudioGenerator

__all__ = ["SceneGenerator", "AudioGenerator"]
