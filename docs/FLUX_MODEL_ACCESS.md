# Flux Model Access - Quick Guide

## 🚨 **Error: Gated Model Access**

If you see: `GatedRepoError: 403 Client Error`

This means the Flux model requires HuggingFace access approval.

---

## ✅ **Solution Options**

### **Option 1: Use Non-Gated Model (EASIEST)**

I've updated the code to use `FLUX.1-dev` which doesn't require approval:

```bash
# Just run it - no approval needed!
python generate_images.py --input path/to/scenes.json
```

**Note**: FLUX.1-dev requires more steps (50 vs 4) but same quality.

---

### **Option 2: Get Schnell Access (FASTER)**

If you want the 4-step Schnell model:

1. **Visit**: https://huggingface.co/black-forest-labs/FLUX.1-schnell

2. **Click** "Request Access" button

3. **Wait** for approval (usually instant)

4. **Login** on server:
```bash
huggingface-cli login
# Paste your token from https://huggingface.co/settings/tokens
```

5. **Update code** to use Schnell:
```python
# In src/image/flux_client.py line 28
model_id: str = "black-forest-labs/FLUX.1-schnell"
```

6. **Update steps**:
```python
# In generate_images.py line 22
DEFAULT_STEPS = 4  # Schnell only needs 4
```

---

### **Option 3: Use Stable Diffusion (ALTERNATIVE)**

If Flux models are too large:

```python
# Replace in flux_client.py
from diffusers import StableDiffusionPipeline

self.pipeline = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=self.dtype
).to(self.device)
```

---

## 📊 **Model Comparison**

| Model | Gated | Steps | VRAM | Speed |
|-------|-------|-------|------|-------|
| FLUX.1-schnell | ✅ Yes | 4 | ~16GB | ⚡ Fast |
| FLUX.1-dev | ❌ No | 50 | ~16GB | 🐌 Slow |
| SD 1.5 | ❌ No | 20-50 | ~4GB | 🚀 Medium |

**Recommendation**: Use FLUX.1-dev (already set as default)

---

## 🧪 **Test It:**

```bash
# Pull latest code
git pull origin main

# Try with dev model (no approval needed)
python generate_images.py --input output/{timestamp}_{topic}/1_scripts/{topic}_scenes.json

# Should work immediately!
```

---

## 💡 **Current Default**

The code now uses **FLUX.1-dev** by default, so you can:

```bash
# This will work without any access approval
python generate_images.py --input your_scenes.json
```

No configuration needed! ✅
