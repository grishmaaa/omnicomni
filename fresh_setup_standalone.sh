#!/bin/bash
#
# OmniComni Fresh Setup Script (Standalone Version)
# No external test files required - everything self-contained
#
# Usage: bash fresh_setup_standalone.sh
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() { echo -e "\n${BLUE}===================================================================${NC}\n${BLUE}$1${NC}\n${BLUE}===================================================================${NC}\n"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

print_header "OmniComni Fresh Setup - Standalone Version"

# ============================================================================
# STEP 0: Critical Disk Space Check
# ============================================================================
print_header "Step 0: Critical Disk Space Check"

available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
print_info "Available disk space: ${available_space}GB"

if [ "$available_space" -lt 30 ]; then
    print_error "CRITICAL: Only ${available_space}GB available!"
    print_error "Models require ~14GB, pipeline needs ~20GB workspace"
    print_error "TOTAL NEEDED: 35GB minimum, 50GB+ recommended"
    echo ""
    print_warning "Options:"
    print_warning "1. Cancel and upgrade to bigger instance (recommended)"
    print_warning "2. Continue with SEVERE space constraints (risky)"
    echo ""
    read -p "Continue anyway? This will likely fail! (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled - Please upgrade to instance with 100GB+ storage"
        exit 1
    fi
fi

# ============================================================================
# STEP 1: Clear Cache (Optional)
# ============================================================================
print_header "Step 1: Cache Management"

if [ -d "$HOME/.cache/huggingface/hub" ]; then
    cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1 || echo "0")
    print_info "Current cache size: $cache_size"
    
    print_warning "Delete cache and re-download models? (~14GB download)"
    read -p "Clear cache? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Clearing cache..."
        rm -rf "$HOME/.cache/huggingface/hub/"*
        print_success "Cache cleared"
    else
        print_info "Keeping existing cache"
    fi
fi

# ============================================================================
# STEP 2: Download Llama Model (~3GB)
# ============================================================================
print_header "Step 2: Downloading Llama Model (~3GB)"

print_info "Testing Llama download..."
python3 << 'LLAMA_TEST'
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

print("Initializing Llama-3.2-3B...")
model_id = "meta-llama/Llama-3.2-3B-Instruct"

try:
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.bfloat16
    )
    
    print("✅ Llama model downloaded and loaded!")
    print(f"Device: {next(model.parameters()).device}")
    
    # Quick test
    inputs = tokenizer("Hello", return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=5)
    print("✅ Generation test passed!")
    
except Exception as e:
    print(f"❌ Llama download failed: {e}")
    sys.exit(1)
LLAMA_TEST

if [ $? -ne 0 ]; then
    print_error "Llama model download failed!"
    exit 1
fi

print_success "Llama model ready"
du -sh "$HOME/.cache/huggingface" 2>/dev/null | awk '{print "Cache size: " $1}'

# ============================================================================
# STEP 3: Download Stable Diffusion (~4GB)
# ============================================================================
print_header "Step 3: Downloading Stable Diffusion (~4GB)"

print_info "Testing SD download..."
python3 << 'SD_TEST'
import sys
import torch
from diffusers import StableDiffusionPipeline

print("Initializing Stable Diffusion 1.5...")
model_id = "runwayml/stable-diffusion-v1-5"

try:
    pipeline = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    )
    
    if torch.cuda.is_available():
        pipeline = pipeline.to("cuda")
    
    print("✅ SD model downloaded!")
    
except Exception as e:
    print(f"❌ SD download failed: {e}")
    sys.exit(1)
SD_TEST

if [ $? -ne 0 ]; then
    print_error "SD model download failed!"
    exit 1
fi

print_success "SD model ready"
du -sh "$HOME/.cache/huggingface" 2>/dev/null | awk '{print "Cache size: " $1}'

# ============================================================================
# STEP 4: Download SVD (~7GB) - LARGEST DOWNLOAD
# ============================================================================
print_header "Step 4: Downloading SVD (~7GB) - This takes longest"

print_warning "This is the largest model download (~7GB)"
print_info "Testing SVD download..."

python3 << 'SVD_TEST'
import sys
import torch
from diffusers import StableVideoDiffusionPipeline

print("Initializing Stable Video Diffusion...")
model_id = "stabilityai/stable-video-diffusion-img2vid-xt-1-1"

try:
    pipeline = StableVideoDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        variant="fp16"
    )
    
    if torch.cuda.is_available():
        pipeline.enable_model_cpu_offload()
    
    print("✅ SVD model downloaded!")
    
except Exception as e:
    print(f"❌ SVD download failed: {e}")
    sys.exit(1)
SVD_TEST

if [ $? -ne 0 ]; then
    print_error "SVD model download failed!"
    print_warning "This might be due to disk space. Check: df -h"
    exit 1
fi

print_success "SVD model ready"
du -sh "$HOME/.cache/huggingface" 2>/dev/null | awk '{print "Cache size: " $1}'

# ============================================================================
# STEP 5: Verify All Models
# ============================================================================
print_header "Step 5: Verification"

models_found=0

if ls "$HOME/.cache/huggingface/hub/models--meta-llama"* 1> /dev/null 2>&1; then
    print_success "Llama cached"
    ((models_found++))
fi

if ls "$HOME/.cache/huggingface/hub/models--runwayml"* 1> /dev/null 2>&1; then
    print_success "SD cached"
    ((models_found++))
fi

if ls "$HOME/.cache/huggingface/hub/models--stabilityai--stable-video"* 1> /dev/null 2>&1; then
    print_success "SVD cached"
    ((models_found++))
fi

print_info "Models found: $models_found/3"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header "Setup Complete!"

cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1)
remaining=$(df -h . | tail -1 | awk '{print $4}')

echo -e "${GREEN}"
cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║                  ✅ Models Downloaded!                         ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Cache size: $cache_size"
print_info "Disk remaining: $remaining"

if [ "$models_found" -eq 3 ]; then
    print_success "All 3 models ready!"
    echo ""
    print_header "Ready to Use!"
    echo "python pipeline_manager.py --topic \"Your Topic\""
else
    print_warning "Only $models_found/3 models cached"
    print_warning "Some downloads may have failed"
fi
