# Task 11: Final Assembly - Complete Guide

## 🎬 What Was Added

**New File:**
- `merge_scenes.py` - Final video+audio assembly CLI

**What It Does:**
- Merges scene videos with audio narration
- **Audio is Master**: Video loops to match audio duration
- Proper codec settings for universal playback
- Batch processing with resume capability

---

## 🎯 **Key Strategy: "Audio is Master"**

### **The Problem:**
- Videos from SVD: ~4 seconds (25 frames @ 6 FPS)
- Audio from TTS: Variable (5-10 seconds)
- Video is usually shorter than audio

### **The Solution:**
```
Audio Duration: 8.2 seconds
Video Duration: 4.1 seconds
Loops Needed: ceil(8.2 / 4.1) = 2

Result: Video plays twice, trimmed to exactly 8.2s
```

---

## 🔧 **Technical Details**

### **Critical: yuv420p Pixel Format**

**Why it matters:**
```python
# Without yuv420p:
# ❌ "Can't play file" on macOS QuickTime
# ❌ "Unsupported format" on Windows Media Player  
# ❌ Playback issues on mobile devices

# With yuv420p:
# ✅ Universal H.264/MP4 standard
# ✅ Works everywhere
```

**What it is:**
- YUV 4:2:0 chroma subsampling
- Standard for H.264 video
- 50% smaller than 4:4:4
- Universally compatible

### **Container Optimization (+faststart)**

```bash
# Regular MP4:
# [metadata at end of file]
# Must download entire file before playback

# With +faststart:
# [metadata at start of file]
# Playback starts immediately (progressive streaming)
```

---

## 📋 **Complete Workflow**

```bash
# Step 1: Generate scenes + audio
python pipeline_manager.py --topic "Cyberpunk Tokyo"
# Output:
#   output/20251210_073941_cyberpunk_tokyo/
#   ├── 1_scripts/cyberpunk_tokyo_scenes.json
#   └── 2_audio/scene_01-06_audio.mp3

# Step 2: Generate images
python generate_images.py --input output/20251210_073941_cyberpunk_tokyo/1_scripts/cyberpunk_tokyo_scenes.json
# Output:
#   output/images/cyberpunk_tokyo_scenes/scene_01_var_01.png

# Step 3: Generate videos
python generate_videos.py --topic cyberpunk_tokyo_scenes
# Output:
#   output/video/clips/cyberpunk_tokyo_scenes/scene_01.mp4

# Step 4: Final assembly (NEW!)
python merge_scenes.py --topic cyberpunk_tokyo_scenes
# Output:
#   output/video/final/cyberpunk_tokyo_scenes/scene_01_final.mp4
```

---

## 🚀 **Usage**

### **Basic:**
```bash
python merge_scenes.py --topic cyberpunk_tokyo_scenes
```

### **Custom Paths:**
```bash
python merge_scenes.py \
    --topic my_topic \
    --video-dir output/video/clips \
    --audio-dir output \
    --output output/final
```

### **Regenerate All:**
```bash
python merge_scenes.py --topic topic --no-skip
```

---

## 📊 **What Happens:**

```
Input:
├── Video: output/video/clips/topic/scene_01.mp4 (4.1s, silent)
└── Audio: output/{timestamp}_topic/2_audio/scene_01_audio.mp3 (8.2s)

Processing:
1. Probe durations: video=4.1s, audio=8.2s
2. Calculate loops: ceil(8.2 / 4.1) = 2
3. Loop video 2 times
4. Trim to exactly 8.2s
5. Merge with audio
6. Encode with H.264 (yuv420p) + AAC

Output:
└── output/video/final/topic/scene_01_final.mp4 (8.2s, with audio)
    - Video loops seamlessly
    - Audio plays once
    - Perfect sync
```

---

## 🎨 **Encoding Settings**

```python
VIDEO:
  Codec:      libx264
  Pixel:      yuv420p    # CRITICAL for compatibility
  Preset:     fast       # Balance quality/speed
  CRF:        23         # Quality (18-28 range)

AUDIO:
  Codec:      AAC
  Bitrate:    192k       # High quality

CONTAINER:
  Format:     MP4
  Flags:      +faststart # Enable streaming
```

---

## 🔍 **Resume Capability**

```bash
# First run: processes scenes 1-5
python merge_scenes.py --topic topic

# Script crashes after scene 3

# Re-run: skips 1-3, continues from 4
python merge_scenes.py --topic topic
# Output:
#   ⏭️  Scene 01: Already exists, skipping
#   ⏭️  Scene 02: Already exists, skipping
#   ⏭️  Scene 03: Already exists, skipping
#   🎬 Scene 04: Processing...
```

---

## ⚠️ **Troubleshooting**

### **"Video not found" Warning:**
```
Scene X: Video file not found
```

**Solution:**
```bash
# Make sure you ran generate_videos.py first
python generate_videos.py --topic your_topic_scenes
```

### **"No audio files found":**
```
No audio files found for topic
```

**Solution:**
```bash
# Topic slug must match audio folder
# Audio is in: output/{timestamp}_topic/2_audio/
# Use the topic name (not the full timestamped folder)
```

### **Videos won't play:**

Check encoding:
```bash
ffprobe scene_01_final.mp4

# Should show:
# Video: h264, yuv420p
# Audio: aac, 192 kb/s
```

---

## 📁 **Output Structure**

```
output/
├── {timestamp}_cyberpunk_tokyo/
│   └── 2_audio/
│       ├── scene_01_audio.mp3
│       └── ...
├── video/
│   ├── clips/
│   │   └── cyberpunk_tokyo_scenes/
│   │       ├── scene_01.mp4 (silent, 4s)
│   │       └── ...
│   └── final/                       ← NEW!
│       └── cyberpunk_tokyo_scenes/
│           ├── scene_01_final.mp4   ← Complete with audio!
│           └── ...
```

---

## ✅ **Follows OmniComni Patterns**

✅ CLI with argparse (matches generate_*.py)  
✅ Uses FFmpegService from src.core  
✅ Comprehensive logging  
✅ Resume capability (skip existing)  
✅ Error resilience (continues on failure)  
✅ Type hints and docstrings  
✅ Batch processing  

---

## 🎉 **Complete Pipeline**

**9 Steps → Final Videos:**

1. ✅ LLM Scene Generation
2. ✅ TTS Audio Narration  
3. ✅ SD Image Generation
4. ✅ SVD Video Animation
5. ✅ Final Assembly ← **YOU ARE HERE!**

**Result:** Complete videos with synced audio, ready for distribution! 🎬
