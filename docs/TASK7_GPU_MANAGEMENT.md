# Task 7: GPU Memory Management - Integration Guide

## 📊 **Architecture Analysis**

### **Approach A: Monolithic (Single Process)**
**What**: Load LLM → generate scenes → unload → load Image model → generate images

**Pros:**
- Single command execution
- Shared state and variables
- Simpler for users

**Cons:**
- Python GC not guaranteed to free memory
- Risk of fragmented VRAM
- One crash loses all progress

### **Approach B: Decoupled Processes ✅ RECOMMENDED**
**What**: Run pipeline_manager.py (LLM) → terminate → run generate_images.py (Image)

**Pros:**
- OS-level memory cleanup (guaranteed)
- Crash isolation (LLM crash doesn't affect images)
- Easier debugging
- Lower risk of OOM

**Cons:**
- Two commands to run
- Intermediate JSON files

**Verdict:** We use **Approach B** - separate scripts for reliability.

---

## 🔧 **What Was Added**

### **1. `src/core/gpu_manager.py`**

**Functions:**
- `get_vram_stats()` - Monitor VRAM usage
- `log_vram_stats()` - Log current VRAM
- `force_cleanup()` - Aggressive memory cleanup
- `cleanup_model()` - Clean specific model
- `check_vram_availability()` - Check before loading

**Utilities:**
- `@managed_execution` - Decorator for auto-cleanup
- `VRAMContext` - Context manager for cleanup

**Usage:**
```python
from src.core.gpu_manager import force_cleanup, log_vram_stats

# After using model
del model
force_cleanup()
log_vram_stats("After cleanup")
```

### **2. `vram_switch_demo.py`**

Proves cleanup works:
- Allocates 4GB "Mock LLM"
- Cleans up
- Allocates 4GB "Mock Image Model"
- Verifies memory freed

**Run it:**
```bash
python vram_switch_demo.py
```

---

## 🎯 **Integration with OUR Pipeline**

### **Option 1: Decoupled (Current - RECOMMENDED)**

```bash
# Step 1: Generate scenes + audio
python pipeline_manager.py --topic "Cyberpunk Tokyo"

# Step 2: Generate images (separate process)
python generate_images.py --input output/{timestamp}_cyberpunk_tokyo/1_scripts/cyberpunk_tokyo_scenes.json

# Memory automatically freed between steps (OS handles it)
```

**Why this works:** Each script runs in separate process. When pipeline_manager.py exits, OS reclaims ALL memory.

### **Option 2: Manual Cleanup (If needed)**

If you want to add cleanup to existing scripts:

#### **A. In `pipeline_manager.py`** (after LLM usage)

Add after line 380 (after scene generation):

```python
from src.core.gpu_manager import cleanup_model

# In ContentPipeline class, after _generate_storyboard():
def run_pipeline(self):
    # ... existing code ...
    
    # Stage 1: Generate storyboard
    scenes = self._generate_storyboard()
    
    # NEW: Cleanup LLM
    cleanup_model(self.model, self.tokenizer)
    self.logger.info("LLM unloaded, VRAM freed")
    
    # Stage 2: Generate audio
    audio_files = self._generate_audio(scenes)
    # ... rest of code ...
```

#### **B. In `generate_images.py`** (if running both in same script)

Add before/after image generation:

```python
from src.core.gpu_manager import log_vram_stats, force_cleanup

def generate_images_for_scenes(...):
    # Log before
    log_vram_stats("Before image generation")
    
    # Initialize generator
    generator = FluxImageGenerator()
    
    # ... generate images ...
    
    # Cleanup after
    generator.unload()
    force_cleanup()
    log_vram_stats("After cleanup")
```

---

## 🧪 **Testing**

### **1. Test Memory Management:**
```bash
python vram_switch_demo.py
# Should show ~4GB freed between "models"
```

### **2. Test Real Pipeline:**
```bash
# Monitor VRAM in separate terminal
watch -n 1 nvidia-smi

# Run pipeline
python pipeline_manager.py --topic "Test"
# Watch VRAM drop to ~0 when finished

python generate_images.py --input output/.../test_scenes.json
# Watch VRAM rise as images load
```

---

## 📋 **When to Use Each Approach**

| Scenario | Use Approach |
|----------|--------------|
| Production server | **B (Decoupled)** - Most reliable |
| Limited VRAM (<12GB) | **B (Decoupled)** - Safest |
| Development/Testing | Either works |
| Single video request | **B (Decoupled)** - Simpler |
| Batch processing | **B (Decoupled)** - Crash isolation |

---

## ✅ **Recommendations**

**For YOUR 4x RTX 4090 setup:**

1. **Keep using Approach B** (separate scripts)
   - Most reliable
   - Already working
   - No code changes needed

2. **Use gpu_manager utilities** for monitoring:
```python
from src.core.gpu_manager import log_vram_stats

# Add to pipeline_manager.py
log_vram_stats("After LLM loading")
log_vram_stats("After scene generation")
```

3. **Run demo** to prove cleanup works:
```bash
python vram_switch_demo.py
```

---

## 🎉 **Summary**

**Task 7 Complete:**
- ✅ GPU memory management utilities
- ✅ Cleanup functions with logging
- ✅ Demo proving it works
- ✅ Integration guide for our codebase

**Current Architecture (Approach B) is OPTIMAL.**  
No changes needed unless you want unified execution!
