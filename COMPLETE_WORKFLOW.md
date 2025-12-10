# OmniComni Pipeline - Complete Workflow Guide

## 🎬 **End-to-End: Topic → Final Video**

This guide walks you through the complete pipeline from a text topic to a final, polished video with audio.

---

## 📋 **Prerequisites**

### **1. Install System Dependencies:**
```bash
# FFmpeg (required for video assembly)
# Linux:
sudo apt install ffmpeg

# Windows:
winget install ffmpeg

# Verify:
ffmpeg -version
```

### **2. Install Python Dependencies:**
```bash
pip install -r requirements.txt
```

### **3. Configure Environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your HuggingFace token
nano .env
```

### **4. Login to HuggingFace:**
```bash
# Login once (stores credentials)
huggingface-cli login

# Accept licenses for gated models:
# - meta-llama/Llama-3.2-3B-Instruct
# - stabilityai/stable-diffusion-v1-5
# - stabilityai/stable-video-diffusion-img2vid-xt-1-1
```

---

## 🚀 **Complete Workflow (5 Steps)**

### **Step 1: Generate Scenes + Audio** ⏱️ ~30s

```bash
python pipeline_manager.py --topic "Northern Lights Adventure"
```

**What it does:**
- Uses Llama LLM to generate 6 scene descriptions
- Creates TTS audio narration for each scene
- Saves structured JSON and MP3 files

**Output:**
```
output/
└── 20251210_081823_northern_lights_adventure/
    ├── 1_scripts/
    │   └── northern_lights_adventure_scenes.json
    ├── 2_audio/
    │   ├── scene_01_audio.mp3
    │   ├── scene_02_audio.mp3
    │   └── ...
    ├── logs/
    │   └── pipeline.log
    └── manifest.json
```

---

### **Step 2: Generate Images** ⏱️ ~60s

```bash
# Use the scenes JSON path from Step 1
python generate_images.py --input output/20251210_081823_northern_lights_adventure/1_scripts/northern_lights_adventure_scenes.json
```

**What it does:**
- Takes scene descriptions from JSON
- Generates AI images using Stable Diffusion
- Creates 1 image per scene (configurable via --variations)

**Output:**
```
output/
└── images/
    └── northern_lights_adventure_scenes/
        ├── scene_01_var_01.png
        ├── scene_02_var_01.png
        └── ...
```

**Tips:**
- Add `--variations 3` to generate multiple options per scene
- Default: 512x512 resolution (SD 1.5)
- GPU required (~4GB VRAM)

---

### **Step 3: Generate Videos** ⏱️ ~5 minutes

```bash
# Topic name matches the IMAGE folder
python generate_videos.py --topic northern_lights_adventure_scenes
```

**What it does:**
- Takes images from Step 2
- Animates them using Stable Video Diffusion
- Creates 25-frame videos (4-5 seconds each)

**Output:**
```
output/
└── video/
    └── clips/
        └── northern_lights_adventure_scenes/
            ├── scene_01.mp4  (silent, ~4s)
            ├── scene_02.mp4
            └── ...
```

**Tips:**
- Requires 8-12GB VRAM (uses CPU offloading)
- Takes ~50s per scene
- Add `--fps 7` for faster playback

---

### **Step 4: Merge Video + Audio** ⏱️ ~2 minutes

```bash
python merge_scenes.py --topic northern_lights_adventure_scenes
```

**What it does:**
- Merges video clips with audio narration
- Loops video to match audio duration (audio is master)
- Creates synced videos with proper codecs

**Output:**
```
output/
└── video/
    └── final/
        └── northern_lights_adventure_scenes/
            ├── scene_01_final.mp4  (with audio, ~8s)
            ├── scene_02_final.mp4
            └── ...
```

**Technical Details:**
- Video loops automatically to fill audio duration
- Encoding: H.264 (yuv420p) + AAC (192k)
- Universal playback compatibility

---

### **Step 5: Concatenate Final Video** ⏱️ ~3 minutes

```bash
python concat_scenes.py --topic northern_lights_adventure_scenes
```

**What it does:**
- Stitches all scene videos into single complete video
- Adds professional fade in/out
- Creates final distribution-ready file

**Output:**
```
output/
└── video/
    └── complete/
        └── northern_lights_adventure_scenes_complete.mp4
```

**Final Result:**
- Single video file
- All scenes in order
- Professional fade in/out
- Ready for YouTube/TikTok/Twitter

---

## 📊 **Quick Reference Commands**

### **Complete Workflow (Copy-Paste):**
```bash
# Step 1: Scenes + Audio
python pipeline_manager.py --topic "Your Amazing Topic"

# Step 2: Images (UPDATE PATH!)
python generate_images.py --input output/YYYYMMDD_HHMMSS_your_amazing_topic/1_scripts/your_amazing_topic_scenes.json

# Step 3: Videos
python generate_videos.py --topic your_amazing_topic_scenes

# Step 4: Merge
python merge_scenes.py --topic your_amazing_topic_scenes

# Step 5: Concatenate
python concat_scenes.py --topic your_amazing_topic_scenes

# Result: output/video/complete/your_amazing_topic_scenes_complete.mp4
```

---

## ⏱️ **Total Time Estimate**

| Step | Time (6 scenes) | GPU Required |
|------|-----------------|--------------|
| 1. Scenes + Audio | ~30s | 2-3GB VRAM |
| 2. Images | ~60s | 4GB VRAM |
| 3. Videos | ~5 min | 8-12GB VRAM |
| 4. Merge | ~2 min | Optional |
| 5. Concatenate | ~3 min | Optional |
| **TOTAL** | **~11 min** | RTX 3090+ recommended |

---

## 🎯 **Tips & Best Practices**

### **Topic Selection:**
```bash
# Good topics (clear visuals, strong narrative):
✅ "Journey Through the Sahara Desert"
✅ "Life in the International Space Station"
✅ "The Making of a Samurai Sword"

# Avoid (too abstract):
❌ "Philosophy of Consciousness"
❌ "Quantum Mechanics Equations"
```

### **GPU Memory Management:**
```bash
# Monitor VRAM:
watch -n 1 nvidia-smi

# If OOM errors:
# - Close other GPU processes
# - Reduce --variations in Step 2
# - Use --fps 7 in Step 3 (fewer frames)
```

### **Resume from Failures:**
```bash
# All scripts skip existing files by default
# If Step 3 crashes after scene 3:
python generate_videos.py --topic topic
# Output:
#   ⏭️  Scene 1: Already exists, skipping
#   ⏭️  Scene 2: Already exists, skipping  
#   ⏭️  Scene 3: Already exists, skipping
#   🎬 Scene 4: Processing...

# Force regenerate:
python generate_videos.py --topic topic --no-skip
```

---

## 📁 **Output Structure**

```
output/
├── 20251210_081823_northern_lights_adventure/  # Step 1
│   ├── 1_scripts/
│   │   └── northern_lights_adventure_scenes.json
│   ├── 2_audio/
│   │   └── scene_*.mp3
│   └── manifest.json
├── images/                                      # Step 2
│   └── northern_lights_adventure_scenes/
│       └── scene_*_var_*.png
└── video/
    ├── clips/                                   # Step 3
    │   └── northern_lights_adventure_scenes/
    │       └── scene_*.mp4 (silent)
    ├── final/                                   # Step 4
    │   └── northern_lights_adventure_scenes/
    │       └── scene_*_final.mp4 (with audio)
    └── complete/                                # Step 5
        └── northern_lights_adventure_scenes_complete.mp4
```

---

## ⚠️ **Troubleshooting**

### **"HuggingFace auth required"**
```bash
huggingface-cli login
# Visit model pages and accept licenses
```

### **"FFmpeg not found"**
```bash
# Install FFmpeg first
sudo apt install ffmpeg  # Linux
winget install ffmpeg    # Windows
```

### **"CUDA out of memory"**
```bash
# Check VRAM usage
nvidia-smi

# Kill other processes
ps aux | grep python
kill <PID>

# Or use smaller settings
python generate_videos.py --topic topic --fps 7
```

### **"No scene clips found"**
```bash
# Check folder names match
ls output/video/final/

# Topic slug must match exactly
python concat_scenes.py --topic <exact_folder_name>
```

---

## 🎬 **Example: Complete Run**

```bash
# 1. Generate content
$ python pipeline_manager.py --topic "Ancient Egypt Mysteries"
✅ Generated 6 scenes
✅ Created 6 audio files
📁 Output: output/20251210_081500_ancient_egypt_mysteries/

# 2. Generate images
$ python generate_images.py --input output/20251210_081500_ancient_egypt_mysteries/1_scripts/ancient_egypt_mysteries_scenes.json
✅ Generated 6 images
📁 Output: output/images/ancient_egypt_mysteries_scenes/

# 3. Animate images
$ python generate_videos.py --topic ancient_egypt_mysteries_scenes
✅ Generated 6 videos (4.2s each)
📁 Output: output/video/clips/ancient_egypt_mysteries_scenes/

# 4. Merge with audio
$ python merge_scenes.py --topic ancient_egypt_mysteries_scenes
✅ Merged 6 videos with audio
📁 Output: output/video/final/ancient_egypt_mysteries_scenes/

# 5. Create final video
$ python concat_scenes.py --topic ancient_egypt_mysteries_scenes
✅ Final video: 47.8s, 85MB
📁 Output: output/video/complete/ancient_egypt_mysteries_scenes_complete.mp4

# Done! 🎉
```

---

## ✅ **Verification Checklist**

After completion, verify:

- [ ] Final video exists: `output/video/complete/*_complete.mp4`
- [ ] Video plays in VLC/browser
- [ ] Audio is synced correctly
- [ ] All scenes present (check duration)
- [ ] Fade in/out visible at start/end
- [ ] File size reasonable (~15-20MB per minute)

---

## 🎓 **Advanced Options**

### **Batch Processing Multiple Topics:**
```bash
# Create topics file
cat > topics.txt << EOF
Ancient Egypt Mysteries
Northern Lights Adventure
Deep Sea Discovery
EOF

# Process all (requires custom script)
while read topic; do
    python pipeline_manager.py --topic "$topic"
done < topics.txt
```

### **Custom Image Variations:**
```bash
# Generate 3 variations per scene
python generate_images.py --input <scenes.json> --variations 3

# Manually select best before video generation
ls output/images/topic_scenes/
# Pick best: scene_01_var_02.png
# Rename to: scene_01_var_01.png (or modify generate_videos.py)
```

### **Custom Video Settings:**
```bash
# Higher motion (more dynamic)
python generate_videos.py --topic topic --motion 180

# Different FPS
python generate_videos.py --topic topic --fps 7
```

---

## 📚 **Related Documentation**

- [SETUP.md](SETUP.md) - Initial installation
- [TASK6_IMAGE_GENERATION.md](TASK6_IMAGE_GENERATION.md) - Image details
- [TASK8_VIDEO_GENERATION.md](TASK8_VIDEO_GENERATION.md) - Video details
- [TASK10_FFMPEG_SETUP.md](TASK10_FFMPEG_SETUP.md) - FFmpeg setup
- [TASK11_FINAL_ASSEMBLY.md](TASK11_FINAL_ASSEMBLY.md) - Merging details
- [TASK12_CONCATENATION.md](TASK12_CONCATENATION.md) - Concatenation details

---

## 🎉 **You're Ready!**

**5 commands → Complete professional video**

Start creating! 🚀
