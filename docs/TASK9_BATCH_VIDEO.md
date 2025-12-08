# Task 9: Batch Video Generation - Guide

## 🎬 What Was Added

**New File:**
- `generate_videos.py` - Batch video generation CLI

**What It Does:**
- Reads all scene images from `output/images/{topic}/`
- Selects best image variant per scene
- Generates animated MP4 using SVD
- **Critical**: Filenames align with audio for merge:
  - Image: `scene_01_var_01.png`
  - Video: `scene_01.mp4` ← matches audio `scene_01.mp3`

---

## 🚀 Usage

### **Basic:**
```bash
# Generate videos for topic
python generate_videos.py --topic cyberpunk_tokyo

# Looks for: output/images/cyberpunk_tokyo/
# Creates:   output/video/clips/cyberpunk_tokyo/
```

### **Custom Settings:**
```bash
# Higher FPS (shorter videos)
python generate_videos.py --topic my_topic --fps 7

# More motion
python generate_videos.py --topic my_topic --motion 180

# Regenerate all (ignore existing)
python generate_videos.py --topic my_topic --no-skip
```

---

## 📊 **Complete Pipeline (All 9 Tasks)**

```bash
# 1. Generate scenes + audio (Task 4)
python pipeline_manager.py --topic "Cyberpunk Tokyo"
# Output: output/{timestamp}_cyberpunk_tokyo/
#   - 1_scripts/cyberpunk_tokyo_scenes.json
#   - 2_audio/*.mp3

# 2. Generate images (Task 6)
python generate_images.py --input output/{timestamp}_cyberpunk_tokyo/1_scripts/cyberpunk_tokyo_scenes.json
# Output: output/images/cyberpunk_tokyo_scenes/*.png

# 3. Generate videos (Task 9 - NEW!)
python generate_videos.py --topic cyberpunk_tokyo_scenes
# Output: output/video/clips/cyberpunk_tokyo_scenes/*.mp4

# Result:
# ✅ Scenes JSON
# ✅ Audio MP3s (scene_01.mp3, scene_02.mp3, ...)
# ✅ Images PNG (scene_01_var_01.png, ...)
# ✅ Videos MP4 (scene_01.mp4, scene_02.mp4, ...) ← NEW!
```

---

## 🎯 **Key Features**

### **1. Filename Alignment (CRITICAL)**
```
Audio:  scene_01.mp3, scene_02.mp3, ...
Video:  scene_01.mp4, scene_02.mp4, ...
```
Allows FFmpeg merge:
```bash
ffmpeg -i scene_01.mp4 -i scene_01.mp3 -c copy -shortest combined_01.mp4
```

### **2. Resume Capability**
```bash
# First run: generates scenes 1-5
python generate_videos.py --topic my_topic

# Crashes after scene 3
# Re-run: skips 1-3, continues from 4
python generate_videos.py --topic my_topic
```

### **3. Error Resilience**
If one scene fails (OOM, etc.), continues with next scene instead of crashing entire batch.

### **4. Best Image Selection**
Automatically picks first variant (var_01) per scene.

**TODO**: Future enhancement - use aesthetic scorer model.

---

## ⚙️ **Framerate Math**

SVD generates **25 frames**:
- **6 FPS**: 25/6 ≈ 4.2 seconds per clip
- **7 FPS**: 25/7 ≈ 3.6 seconds per clip

**Trade-off:**
- Lower FPS (6) = Smoother motion, longer videos
- Higher FPS (7) = Faster playback, shorter videos

**Recommendation**: Use 6 FPS for balanced results.

---

## 📁 **Directory Structure**

```
output/
├── images/
│   └── cyberpunk_tokyo/
│       ├── scene_01_var_01.png
│       ├── scene_02_var_01.png
│       └── ...
└── video/
    └── clips/
        └── cyberpunk_tokyo/
            ├── scene_01.mp4  ← NEW!
            ├── scene_02.mp4
            └── ...
```

---

## 🎨 **Motion Settings**

**motion_bucket_id** (1-255):
- **50-80**: Subtle (gentle camera movement)
- **127**: Balanced (default)
- **180-255**: High motion (dynamic object movement)

---

## ✅ **Follows OmniComni Patterns**

✅ Matches generate_audio.py/generate_images.py CLI style  
✅ Uses src.core.gpu_manager for VRAM  
✅ Comprehensive logging  
✅ Error resilience (continues on failure)  
✅ Resume capability (skip existing)  
✅ Type hints and docstrings  

---

## 🎉 **Task 9 Complete!**

You now have **complete multimedia generation**:
1. ✅ Text → Scenes (LLM)
2. ✅ Scenes → Audio (TTS)
3. ✅ Text → Images (SD)
4. ✅ Images → Videos (SVD)

**Ready for final merge!** 🎬
