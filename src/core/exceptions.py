"""Custom exceptions for production error handling"""


class PipelineError(Exception):
    """Base exception for all pipeline errors"""
    pass


class LLMGenerationError(PipelineError):
    """Raised when LLM generation fails after all retries"""
    pass


class TTSGenerationError(PipelineError):
    """Raised when TTS audio generation fails"""
    pass


class ValidationError(PipelineError):
    """Raised when scene validation fails"""
    pass


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid"""
    pass
