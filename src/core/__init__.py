"""Package initialization for src.core with GPU utilities"""

from src.core.config import settings
from src.core.models import SceneModel, StoryboardModel, validate_llm_output
from src.core.exceptions import (
    PipelineError,
    LLMGenerationError,
    TTSGenerationError,
    ValidationError,
    ConfigurationError
)
from src.core.gpu_manager import (
    force_cleanup,
    cleanup_model,
    get_vram_stats,
    log_vram_stats,
    check_vram_availability,
    managed_execution,
    VRAMContext
)

__all__ = [
    # Config
    'settings',
    # Models
    'SceneModel',
    'StoryboardModel',
    'validate_llm_output',
    # Exceptions
    'PipelineError',
    'LLMGenerationError',
    'TTSGenerationError',
    'ValidationError',
    'ConfigurationError',
    # GPU Management
    'force_cleanup',
    'cleanup_model',
    'get_vram_stats',
    'log_vram_stats',
    'check_vram_availability',
    'managed_execution',
    'VRAMContext',
]
