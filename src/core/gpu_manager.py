"""
GPU Memory Management Utilities

Handles VRAM lifecycle for multi-model pipelines.
Critical for running LLM + Image generation on limited VRAM.

Architecture Decision:
- Approach A (Monolithic): Load/unload in same process
- Approach B (Decoupled): Separate processes (RECOMMENDED)

We use Approach B (pipeline_manager.py → generate_images.py)
but provide utilities for Approach A flexibility.
"""

import gc
import logging
from typing import Optional, Callable
from functools import wraps
import torch


logger = logging.getLogger(__name__)


# ============================================================================
# VRAM MONITORING
# ============================================================================

def get_vram_stats() -> dict:
    """
    Get current VRAM statistics
    
    Returns:
        Dictionary with VRAM metrics (GB)
        
    Example:
        >>> stats = get_vram_stats()
        >>> print(f"Allocated: {stats['allocated']:.2f}GB")
    """
    if not torch.cuda.is_available():
        return {
            "available": False,
            "total": 0.0,
            "reserved": 0.0,
            "allocated": 0.0,
            "free": 0.0
        }
    
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    reserved = torch.cuda.memory_reserved(0) / 1e9
    allocated = torch.cuda.memory_allocated(0) / 1e9
    free = total - allocated
    
    return {
        "available": True,
        "total": total,
        "reserved": reserved,
        "allocated": allocated,
        "free": free
    }


def log_vram_stats(prefix: str = "VRAM"):
    """
    Log current VRAM statistics
    
    Args:
        prefix: Log message prefix
    """
    stats = get_vram_stats()
    
    if not stats["available"]:
        logger.debug(f"{prefix}: CUDA not available")
        return
    
    logger.info(
        f"{prefix}: {stats['allocated']:.2f}GB / {stats['total']:.2f}GB "
        f"({stats['free']:.2f}GB free)"
    )


# ============================================================================
# MEMORY CLEANUP
# ============================================================================

def force_cleanup():
    """
    Aggressively free VRAM
    
    Why this order matters:
    1. gc.collect() - Collects Python cyclic references
       (models may have circular refs keeping them alive)
    2. torch.cuda.empty_cache() - Releases PyTorch's cached memory
       (allocator doesn't return memory to OS without this)
    3. torch.cuda.ipc_collect() - Cleans up IPC handles
       (multi-GPU or shared memory cleanup)
    
    Business reason: Models can consume 10-20GB VRAM. Without proper
    cleanup, attempting to load a second model causes OOM crashes.
    
    Example:
        >>> # After using LLM
        >>> del model
        >>> del tokenizer
        >>> force_cleanup()
        >>> # Now safe to load image model
    """
    logger.info("🧹 Starting aggressive VRAM cleanup...")
    
    # Log before cleanup
    before_stats = get_vram_stats()
    if before_stats["available"]:
        logger.debug(f"Before cleanup: {before_stats['allocated']:.2f}GB allocated")
    
    # Step 1: Python garbage collection
    # Collects objects with circular references (model graphs often have these)
    logger.debug("Running gc.collect()...")
    collected = gc.collect()
    logger.debug(f"Collected {collected} Python objects")
    
    if torch.cuda.is_available():
        # Step 2: Empty PyTorch CUDA cache
        # Frees memory allocator is holding but not using
        logger.debug("Running torch.cuda.empty_cache()...")
        torch.cuda.empty_cache()
        
        # Step 3: IPC cleanup (for multi-GPU or shared memory)
        logger.debug("Running torch.cuda.ipc_collect()...")
        torch.cuda.ipc_collect()
    
    # Log after cleanup
    after_stats = get_vram_stats()
    if after_stats["available"]:
        freed = before_stats["allocated"] - after_stats["allocated"]
        logger.info(f"✅ Cleanup complete: Freed {freed:.2f}GB VRAM")
        logger.info(f"   After: {after_stats['allocated']:.2f}GB / {after_stats['total']:.2f}GB")
    else:
        logger.info("✅ Cleanup complete (CPU mode)")


def cleanup_model(model, tokenizer=None):
    """
    Clean up a specific model and tokenizer
    
    Args:
        model: Model object to delete
        tokenizer: Optional tokenizer to delete
        
    Example:
        >>> cleanup_model(llm_model, llm_tokenizer)
        >>> # Memory freed, safe to load next model
    """
    logger.info("Unloading model from memory...")
    
    # Delete references
    if model is not None:
        del model
    if tokenizer is not None:
        del tokenizer
    
    # Force cleanup
    force_cleanup()


# ============================================================================
# MANAGED EXECUTION
# ============================================================================

def managed_execution(func: Callable):
    """
    Decorator to automatically cleanup after function execution
    
    Ensures VRAM is freed even if function raises an exception.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with automatic cleanup
        
    Example:
        @managed_execution
        def generate_scenes(topic):
            model = load_llm()
            return model.generate(topic)
        # Cleanup happens automatically after return
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Starting managed execution: {func.__name__}")
            log_vram_stats("Before execution")
            
            result = func(*args, **kwargs)
            
            return result
        finally:
            # Always cleanup, even on exception
            logger.debug(f"Cleaning up after: {func.__name__}")
            force_cleanup()
            log_vram_stats("After cleanup")
    
    return wrapper


class VRAMContext:
    """
    Context manager for VRAM lifecycle
    
    Example:
        with VRAMContext("LLM Generation"):
            model = load_llm()
            result = model.generate()
        # Cleanup happens automatically
    """
    
    def __init__(self, name: str = "Operation"):
        """
        Initialize context
        
        Args:
            name: Operation name for logging
        """
        self.name = name
    
    def __enter__(self):
        logger.info(f"Starting: {self.name}")
        log_vram_stats(f"{self.name} - Before")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info(f"Cleaning up: {self.name}")
        force_cleanup()
        log_vram_stats(f"{self.name} - After")
        return False  # Don't suppress exceptions


# ============================================================================
# EDGE CASE HANDLING
# ============================================================================

def safe_cleanup():
    """
    Cleanup with CPU fallback (no-op if no CUDA)
    
    Use this when CUDA availability is uncertain
    """
    try:
        force_cleanup()
    except Exception as e:
        logger.warning(f"Cleanup failed (CPU mode?): {e}")


def check_vram_availability(required_gb: float) -> bool:
    """
    Check if sufficient VRAM is available
    
    Args:
        required_gb: Required VRAM in GB
        
    Returns:
        True if sufficient VRAM available
        
    Example:
        >>> if check_vram_availability(8.0):
        ...     load_large_model()
        ... else:
        ...     logger.error("Insufficient VRAM")
    """
    stats = get_vram_stats()
    
    if not stats["available"]:
        logger.warning("CUDA not available, cannot check VRAM")
        return False
    
    available = stats["free"]
    sufficient = available >= required_gb
    
    if not sufficient:
        logger.warning(
            f"Insufficient VRAM: need {required_gb:.1f}GB, "
            f"have {available:.1f}GB free"
        )
    
    return sufficient
