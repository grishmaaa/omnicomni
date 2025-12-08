#!/usr/bin/env python3
"""
Robust Llama-3.2-3B-Instruct Test Script
Tests model loading with device detection and proper error handling
"""

import os
import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from pathlib import Path


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def check_authentication():
    """Check for HuggingFace authentication"""
    print_section("🔐 STEP 1: Authentication Check")
    
    # Check for token in various locations
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    env_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    
    if token_file.exists():
        print("✅ HuggingFace token found in cache")
        return True
    elif env_token:
        print("✅ HuggingFace token found in environment")
        return True
    else:
        print("❌ No HuggingFace token found!")
        print("\n📝 How to authenticate:")
        print("  1. Get token from: https://huggingface.co/settings/tokens")
        print("  2. Run: huggingface-cli login")
        print("  3. Or set environment variable:")
        print("       export HF_TOKEN='your_token_here'  # Linux/Mac")
        print("       $env:HF_TOKEN='your_token_here'    # Windows PowerShell")
        print("\n⚠️  You also need to request access to Llama models:")
        print("     https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct")
        
        # Prompt for token input
        print("\n" + "-"*70)
        response = input("Do you want to enter your token now? (y/N): ").strip().lower()
        if response == 'y':
            token = input("Paste your HuggingFace token: ").strip()
            if token:
                os.environ["HF_TOKEN"] = token
                print("✅ Token set for this session")
                return True
        
        print("\n❌ Cannot proceed without authentication. Exiting.")
        return False


def detect_device():
    """Detect and print device information"""
    print_section("🖥️  STEP 2: Device Detection")
    
    if not torch.cuda.is_available():
        print("⚠️  WARNING: CUDA not available!")
        print("   Running on CPU - this will be VERY slow")
        print("   Model loading will use float32 (no quantization)")
        print("\n💡 To use GPU:")
        print("   - Ensure NVIDIA drivers are installed")
        print("   - Install PyTorch with CUDA:")
        print("     pip install torch --index-url https://download.pytorch.org/whl/cu118")
        return "cpu", None
    
    # CUDA is available
    device = torch.cuda.current_device()
    gpu_name = torch.cuda.get_device_name(device)
    total_memory = torch.cuda.get_device_properties(device).total_memory / 1e9
    cuda_version = torch.version.cuda
    
    print(f"✅ CUDA Available")
    print(f"   Device: {gpu_name}")
    print(f"   CUDA Version: {cuda_version}")
    print(f"   Total VRAM: {total_memory:.2f} GB")
    print(f"   PyTorch Version: {torch.__version__}")
    
    # Check if enough VRAM
    if total_memory < 6:
        print(f"\n⚠️  WARNING: Only {total_memory:.2f}GB VRAM available")
        print("   Using 4-bit quantization to fit model")
    else:
        print(f"\n✅ Sufficient VRAM ({total_memory:.2f}GB) for 4-bit loading")
    
    return "cuda", total_memory


def load_model(device_type, vram_gb):
    """Load Llama model with appropriate configuration"""
    print_section("📦 STEP 3: Model Loading")
    
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    print(f"Loading: {model_name}")
    
    try:
        # Load tokenizer
        print("\n1/2 Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✅ Tokenizer loaded")
        
        # Load model based on device
        print("\n2/2 Loading model...")
        
        if device_type == "cuda":
            # GPU: Use 4-bit quantization to save VRAM
            print("   Using 4-bit NF4 quantization (saves VRAM)")
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            # Print VRAM usage
            allocated = torch.cuda.memory_allocated(0) / 1e9
            reserved = torch.cuda.memory_reserved(0) / 1e9
            print(f"✅ Model loaded on GPU")
            print(f"   VRAM Used: {allocated:.2f} GB")
            print(f"   VRAM Reserved: {reserved:.2f} GB")
            
        else:
            # CPU: No quantization (bitsandbytes is GPU-only)
            print("   Using float32 on CPU (no quantization)")
            print("   ⚠️  This will be slow and memory-intensive!")
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            print(f"✅ Model loaded on CPU")
        
        return tokenizer, model
        
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        
        # Common error handling
        error_str = str(e).lower()
        
        if "403" in error_str or "authorization" in error_str:
            print("\n🔒 Authorization Error:")
            print("   1. Ensure you're logged in: huggingface-cli login")
            print("   2. Request access: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct")
            print("   3. Wait for approval (usually instant)")
            
        elif "out of memory" in error_str or "oom" in error_str:
            print("\n💾 Out of Memory Error:")
            print("   Your GPU doesn't have enough VRAM.")
            print("   Solutions:")
            print("   1. Close other GPU applications")
            print("   2. Use 8-bit instead of 4-bit (edit this script)")
            print("   3. Enable CPU offload (advanced)")
            
        elif "dll" in error_str and sys.platform == "win32":
            print("\n🪟 Windows DLL Error:")
            print("   bitsandbytes issue detected.")
            print("   Solutions:")
            print("   1. Install: pip install bitsandbytes-windows")
            print("   2. Or try: pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl")
            print("   3. Install Visual C++ Redistributable:")
            print("      https://aka.ms/vs/17/release/vc_redist.x64.exe")
        
        return None, None


def run_inference(tokenizer, model, device_type):
    """Run test inference"""
    print_section("🎬 STEP 4: Test Inference")
    
    # Test prompt
    prompt = "You are a creative director. Pitch a movie about a cybernetic cat in one sentence."
    
    print(f"📝 Prompt:")
    print(f"   {prompt}")
    
    # Prepare input
    inputs = tokenizer(prompt, return_tensors="pt")
    
    if device_type == "cuda":
        inputs = inputs.to("cuda")
    
    # Generate
    print("\n⚙️  Generating response...")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the response (after the prompt)
    response = generated_text[len(prompt):].strip()
    
    print(f"\n🤖 Generated Response:")
    print(f"   {response}")
    
    # Print VRAM if GPU
    if device_type == "cuda":
        allocated = torch.cuda.memory_allocated(0) / 1e9
        print(f"\n📊 VRAM after generation: {allocated:.2f} GB")


def main():
    """Main test sequence"""
    print("\n" + "🎛️ "*20)
    print("   LLAMA-3.2-3B-INSTRUCT ROBUST TEST SCRIPT")
    print("🎛️ "*20)
    
    # Step 1: Authentication
    if not check_authentication():
        sys.exit(1)
    
    # Step 2: Device Detection
    device_type, vram_gb = detect_device()
    
    # Step 3: Model Loading
    tokenizer, model = load_model(device_type, vram_gb)
    
    if tokenizer is None or model is None:
        print("\n❌ Model loading failed. See errors above.")
        sys.exit(1)
    
    # Step 4: Inference
    try:
        run_inference(tokenizer, model, device_type)
    except Exception as e:
        print(f"\n❌ Inference error: {e}")
        sys.exit(1)
    
    # Success
    print_section("✅ SUCCESS!")
    print("All tests passed! Your environment is ready.")
    print("\nNext steps:")
    print("  1. Run: python main.py \"Your topic here\"")
    print("  2. Monitor VRAM: nvidia-smi  (in another terminal)")
    print("  3. Check output/ folder for results")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
