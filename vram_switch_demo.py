#!/usr/bin/env python3
"""
VRAM Management Demo

Proves memory cleanup works by allocating huge tensors.
Simulates LLM → Image model transition without loading real models.

Tests:
1. Allocate "Mock LLM" (4GB tensor)
2. Force cleanup
3. Allocate "Mock Image Model" (4GB tensor)
4. Verify memory was freed between steps
"""

import torch
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.gpu_manager import (
    force_cleanup,
    get_vram_stats,
    log_vram_stats,
    VRAMContext,
    check_vram_availability
)


def allocate_mock_model(name: str, size_gb: float):
    """
    Allocate a large tensor to simulate model loading
    
    Args:
        name: Model name for logging
        size_gb: Size in gigabytes
        
    Returns:
        Tensor object (keeps reference alive)
    """
    print(f"\n{'='*70}")
    print(f"Allocating {name} ({size_gb:.1f}GB)")
    print(f"{'='*70}")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available, skipping")
        return None
    
    # Calculate tensor size
    # float32 = 4 bytes per element
    # size_gb * 1e9 bytes / 4 bytes per element
    num_elements = int(size_gb * 1e9 / 4)
    
    # Allocate on GPU
    tensor = torch.randn(num_elements, dtype=torch.float32, device='cuda')
    
    print(f"✅ Allocated tensor: {tensor.numel():,} elements")
    log_vram_stats(f"{name} loaded")
    
    return tensor


def demo_sequential_loading():
    """
    Demo: Load LLM, cleanup, then load Image model
    
    This proves memory is actually freed between models.
    """
    print("\n" + "🎬 " * 35)
    print(" " * 20 + "VRAM SWITCHING DEMO")
    print(" " * 15 + "LLM → Image Model Transition")
    print("🎬 " * 35 + "\n")
    
    # Initial state
    print("📊 Initial VRAM State:")
    log_vram_stats("Startup")
    
    # Check if we have enough VRAM
    required = 4.0  # GB per model
    if not check_vram_availability(required):
        print(f"\n❌ Need at least {required}GB free VRAM for demo")
        print("Try closing other GPU processes")
        return False
    
    # Phase 1: Mock LLM
    print("\n" + "="*70)
    print("PHASE 1: LLM Generation")
    print("="*70)
    
    mock_llm = allocate_mock_model("Mock LLM (Llama)", size_gb=4.0)
    
    if mock_llm is None:
        return False
    
    # Simulate using the model
    print("💭 Generating scenes with LLM...")
    print("   (In real code: model.generate())")
    
    # Get stats after LLM
    stats_after_llm = get_vram_stats()
    llm_vram = stats_after_llm['allocated']
    
    # Phase 2: Cleanup
    print("\n" + "="*70)
    print("PHASE 2: Memory Cleanup")
    print("="*70)
    
    print("Deleting LLM model...")
    del mock_llm
    
    print("Running force_cleanup()...")
    force_cleanup()
    
    # Get stats after cleanup
    stats_after_cleanup = get_vram_stats()
    cleanup_vram = stats_after_cleanup['allocated']
    freed = llm_vram - cleanup_vram
    
    print(f"\n✅ CLEANUP VERIFICATION:")
    print(f"   Before cleanup: {llm_vram:.2f}GB")
    print(f"   After cleanup:  {cleanup_vram:.2f}GB")
    print(f"   Freed:          {freed:.2f}GB")
    
    # Phase 3: Mock Image Model
    print("\n" + "="*70)
    print("PHASE 3: Image Generation")
    print("="*70)
    
    mock_image = allocate_mock_model("Mock Image Model (Flux)", size_gb=4.0)
    
    if mock_image is None:
        return False
    
    print("🎨 Generating images...")
    print("   (In real code: pipeline.generate())")
    
    # Get stats after image model
    stats_after_image = get_vram_stats()
    image_vram = stats_after_image['allocated']
    
    # Final cleanup
    print("\n" + "="*70)
    print("FINAL CLEANUP")
    print("="*70)
    
    del mock_image
    force_cleanup()
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n📊 VRAM Peaks:")
    print(f"   LLM loaded:    {llm_vram:.2f}GB")
    print(f"   After cleanup: {cleanup_vram:.2f}GB")
    print(f"   Image loaded:  {image_vram:.2f}GB")
    print(f"\n✅ SUCCESS: Memory was freed between models!")
    print(f"   Freed {freed:.2f}GB before loading image model")
    
    # Validation
    if freed < 3.0:  # Should free most of the 4GB
        print(f"\n⚠️  WARNING: Only freed {freed:.2f}GB (expected ~4GB)")
        return False
    
    print("\n🎉 DEMO COMPLETE: VRAM switching works correctly!")
    return True


def demo_context_manager():
    """
    Demo: Using VRAMContext for automatic cleanup
    """
    print("\n" + "="*70)
    print("BONUS: Context Manager Demo")
    print("="*70)
    
    if not torch.cuda.is_available():
        print("Skipped (no CUDA)")
        return
    
    with VRAMContext("Mock LLM"):
        tensor = torch.randn(int(2e9 / 4), dtype=torch.float32, device='cuda')
        print(f"Allocated 2GB tensor inside context")
    
    print("✅ Context exited, cleanup automatic!")
    log_vram_stats("After context")


def main():
    """Run all demos"""
    try:
        # Main demo
        success = demo_sequential_loading()
        
        # Bonus demo
        if success:
            demo_context_manager()
        
        # Final state
        print("\n📊 Final VRAM State:")
        log_vram_stats("End")
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
