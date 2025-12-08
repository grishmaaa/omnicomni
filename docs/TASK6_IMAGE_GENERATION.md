# Task 6: Image Generation - Quick Guide

## 🎨 What Was Added

**New Files:**
- `src/image/flux_client.py` - Flux-Schnell wrapper
- `generate_images.py` - CLI for image generation

**Updated:**
- `requirements.txt` - Added diffusers, Pillow

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Flux dependencies
pip install diffusers safetensors Pillow

# OR install all at once
pip install -r requirements.txt
```

### 2. Generate Images
```bash
# From pipeline output
python generate_images.py --input output/20241208_073941_topic_3/1_scripts/topic_3_scenes.json

# With multiple variations
python generate_images.py --input scenes.json --variations 3

# Custom output
python generate_images.py --input scenes.json --output my_images
```

---

## 📋 Complete Video Pipeline

```bash
# 1. Generate scenes + audio (Task 4)
python pipeline_manager.py --topic "Cyberpunk Tokyo"
# Output: output/{timestamp}_cyberpunk_tokyo/

# 2. Generate images (Task 6)
python generate_images.py --input output/{timestamp}_cyberpunk_tokyo/1_scripts/cyberpunk_tokyo_scenes.json
# Output: output/images/cyberpunk_tokyo/scene_01_var_01.png

# 3. Results:
# - Scenes JSON
# - Audio MP3s
# - Images PNG ✅ NEW!
```

---

## ⚙️ Configuration

**Default Settings:**
- Model: `black-forest-labs/FLUX.1-schnell`
- Steps: 4 (optimized for Schnell)
- Size: 1024x1024
- Variations: 1 per scene
- Seed: 42 (reproducible)

**Modify:**
```python
# In generate_images.py
DEFAULT_NUM_VARIATIONS = 3  # More variations
DEFAULT_SIZE = 2048  # Larger images
```

---

## 🎯 Follows OmniComni Patterns

✅ Matches `generate_audio.py` CLI structure  
✅ Reads pipeline_manager.py output  
✅ Uses pathlib  
✅ Comprehensive logging  
✅ Error handling (CUDA OOM)  
✅ argparse CLI  

**Ready to use!** No breaking changes to existing code.
