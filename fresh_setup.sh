#!/bin/bash
#
# OmniComni Fresh Setup Script
# Automatically clears cache, downloads models, and verifies installation
#
# Usage: bash fresh_setup.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}===================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running in project directory
if [ ! -f "pipeline_manager.py" ]; then
    print_error "Must run from project root directory!"
    exit 1
fi

print_header "OmniComni Fresh Setup - Automated Installation"

# ============================================================================
# STEP 0: Disk Space Check
# ============================================================================
print_header "Step 0: Checking Disk Space"

available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
print_info "Available disk space: ${available_space}GB"

if [ "$available_space" -lt 50 ]; then
    print_warning "Low disk space detected (${available_space}GB available)"
    print_warning "Recommended: 100GB+ for comfortable operation"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled"
        exit 1
    fi
else
    print_success "Sufficient disk space: ${available_space}GB"
fi

# ============================================================================
# STEP 1: Clear HuggingFace Cache
# ============================================================================
print_header "Step 1: Clearing HuggingFace Cache"

if [ -d "$HOME/.cache/huggingface" ]; then
    cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1 || echo "0")
    print_info "Current cache size: $cache_size"
    
    print_warning "This will delete ALL cached models!"
    print_warning "Models will be re-downloaded (one-time, ~14GB)"
    read -p "Proceed with cache cleanup? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing cache..."
        rm -rf "$HOME/.cache/huggingface/hub/"*
        print_success "Cache cleared"
    else
        print_info "Skipping cache cleanup"
    fi
else
    print_info "No existing cache found"
fi

# ============================================================================
# STEP 2: Download Llama Model (3GB)
# ============================================================================
print_header "Step 2: Downloading Llama Model (~3GB)"

print_info "Testing Llama-3.2-3B download and inference..."
python test_llama.py

if [ $? -eq 0 ]; then
    print_success "Llama model downloaded and verified"
else
    print_error "Llama model download failed"
    exit 1
fi

# Check cache size
cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1 || echo "0")
print_info "Cache size after Llama: $cache_size"

# ============================================================================
# STEP 3: Download Stable Diffusion (4GB)
# ============================================================================
print_header "Step 3: Downloading Stable Diffusion (~4GB)"

print_info "Testing SD 1.5 download..."
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.image.sd_client import SDImageGenerator

print("Initializing Stable Diffusion 1.5...")
try:
    generator = SDImageGenerator()
    print("✅ SD model downloaded and cached!")
    
    # Quick test
    test_img = Path("test_sd_output.png")
    generator.generate(
        prompt="a beautiful landscape",
        output_path=test_img,
        num_inference_steps=10
    )
    print(f"✅ Test image generated: {test_img}")
    
except Exception as e:
    print(f"❌ SD download failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Stable Diffusion downloaded and verified"
    rm -f test_sd_output.png
else
    print_error "Stable Diffusion download failed"
    exit 1
fi

cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1 || echo "0")
print_info "Cache size after SD: $cache_size"

# ============================================================================
# STEP 4: Download Stable Video Diffusion (7GB)
# ============================================================================
print_header "Step 4: Downloading Stable Video Diffusion (~7GB)"

print_info "Testing SVD download (this takes longest)..."
python tests/test_svd.py

if [ $? -eq 0 ]; then
    print_success "SVD model downloaded and verified"
    rm -f test_output.mp4 test_image.png
else
    print_error "SVD download failed"
    exit 1
fi

cache_size=$(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1 || echo "0")
print_info "Cache size after SVD: $cache_size"

# ============================================================================
# STEP 5: Verify Installation
# ============================================================================
print_header "Step 5: Verifying Complete Installation"

# Check cache contents
print_info "Checking cached models..."

models_found=0

if [ -d "$HOME/.cache/huggingface/hub/models--meta-llama"* ]; then
    print_success "Llama model cached"
    ((models_found++))
else
    print_error "Llama model NOT found in cache"
fi

if [ -d "$HOME/.cache/huggingface/hub/models--runwayml--stable-diffusion"* ]; then
    print_success "Stable Diffusion model cached"
    ((models_found++))
else
    print_error "Stable Diffusion model NOT found in cache"
fi

if [ -d "$HOME/.cache/huggingface/hub/models--stabilityai--stable-video"* ]; then
    print_success "SVD model cached"
    ((models_found++))
else
    print_error "SVD model NOT found in cache"
fi

if [ $models_found -eq 3 ]; then
    print_success "All models verified in cache!"
else
    print_warning "Only $models_found/3 models found"
fi

# Final stats
print_info "Final cache size: $(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1)"
print_info "Disk space remaining: $(df -h . | tail -1 | awk '{print $4}')"

# ============================================================================
# STEP 6: Create Test Output
# ============================================================================
print_header "Step 6: Running End-to-End Test"

print_info "Testing complete pipeline with small example..."

# Run a quick test
python pipeline_manager.py --topic "Setup Test" || {
    print_error "Pipeline test failed"
    exit 1
}

print_success "Pipeline test successful!"

# Find the output
latest_output=$(ls -td output/*_setup_test 2>/dev/null | head -1)
if [ -n "$latest_output" ]; then
    print_success "Test output created: $latest_output"
    
    # Check scenes
    if [ -f "$latest_output/1_scripts/setup_test_scenes.json" ]; then
        print_success "Scenes generated"
    fi
    
    # Check audio
    audio_count=$(ls "$latest_output/2_audio/"*.mp3 2>/dev/null | wc -l)
    print_success "Audio files generated: $audio_count"
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header "Setup Complete! 🎉"

echo -e "${GREEN}"
cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║                  ✅ Setup Successful!                          ║
║                                                                ║
║  All models downloaded and cached:                            ║
║  - Llama-3.2-3B (Scene Generation)                            ║
║  - Stable Diffusion 1.5 (Image Generation)                    ║
║  - Stable Video Diffusion (Video Animation)                   ║
║                                                                ║
║  Future runs will use cached models (no re-download)          ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

print_info "Cache location: $HOME/.cache/huggingface/"
print_info "Cache size: $(du -sh "$HOME/.cache/huggingface" 2>/dev/null | cut -f1)"

print_header "Next Steps"

echo "Run the complete workflow:"
echo ""
echo "  # 1. Generate scenes + audio"
echo "  python pipeline_manager.py --topic \"Your Topic\""
echo ""
echo "  # 2. Generate images"
echo "  python generate_images.py --input output/{timestamp}_your_topic/1_scripts/your_topic_scenes.json"
echo ""
echo "  # 3. Generate videos"
echo "  python generate_videos.py --topic your_topic_scenes"
echo ""
echo "  # 4. Merge video + audio"
echo "  python merge_scenes.py --topic your_topic_scenes"
echo ""
echo "  # 5. Create final video"
echo "  python concat_scenes.py --topic your_topic_scenes"
echo ""

print_success "Setup complete! Ready to create videos! 🎬"
