#!/usr/bin/env python3
"""
Simple verification script to check environment setup
"""

import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✅ torch {torch.__version__}")
    except ImportError as e:
        print(f"❌ torch: {e}")
        return False
    
    try:
        import transformers
        print(f"✅ transformers {transformers.__version__}")
    except ImportError as e:
        print(f"❌ transformers: {e}")
        return False
    
    try:
        import bitsandbytes
        print(f"✅ bitsandbytes")
    except ImportError as e:
        print(f"❌ bitsandbytes: {e}")
        print("   Windows users: try 'pip install bitsandbytes-windows'")
        return False
    
    try:
        import accelerate
        print(f"✅ accelerate")
    except ImportError as e:
        print(f"❌ accelerate: {e}")
        return False
    
    try:
        import edge_tts
        print(f"✅ edge-tts")
    except ImportError as e:
        print(f"❌ edge-tts: {e}")
        return False
    
    return True


def test_cuda():
    """Test CUDA availability"""
    import torch
    
    print("\nTesting CUDA...")
    
    if not torch.cuda.is_available():
        print("⚠️  CUDA not available - will run on CPU (very slow)")
        print("   Install CUDA-enabled PyTorch:")
        print("   pip install torch --index-url https://download.pytorch.org/whl/cu118")
        return False
    
    print(f"✅ CUDA available")
    print(f"   Version: {torch.version.cuda}")
    print(f"   Device: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    return True


def main():
    print("="*60)
    print("ENVIRONMENT VERIFICATION")
    print("="*60 + "\n")
    
    imports_ok = test_imports()
    cuda_ok = test_cuda()
    
    print("\n" + "="*60)
    if imports_ok and cuda_ok:
        print("✅ ALL CHECKS PASSED")
        print("\nYou're ready to run:")
        print("  python test_llama.py")
    elif imports_ok:
        print("⚠️  IMPORTS OK, CUDA NOT AVAILABLE")
        print("\nYou can run on CPU (slow):")
        print("  python test_llama.py")
    else:
        print("❌ SETUP INCOMPLETE")
        print("\nSee SETUP.md for detailed instructions")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
