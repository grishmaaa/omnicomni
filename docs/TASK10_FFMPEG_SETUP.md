# Task 10: FFmpeg Integration - Installation & Usage Guide

## 🎬 What Was Added

**New Files:**
- `src/core/ffmpeg_service.py` - FFmpeg wrapper service
- `tests/test_ffmpeg.py` - Environment validation script

**What It Does:**
- Validates FFmpeg installation (fail-fast)
- Extracts video metadata
- Extracts audio from video
- Merges video + audio
- Generates test videos

---

## 📦 **FFmpeg Installation**

### **Linux (Ubuntu/Debian):**
```bash
# Install FFmpeg
sudo apt update
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
ffprobe -version

# Should show version info (4.x or 5.x+)
```

### **Windows:**

#### **Option 1: Winget (Recommended)**
```powershell
# Install via Windows Package Manager
winget install ffmpeg

# Restart terminal, then verify
ffmpeg -version
```

#### **Option 2: Manual Install**
1. **Download**: https://github.com/BtbN/FFmpeg-Builds/releases
   - Get: `ffmpeg-master-latest-win64-gpl.zip`

2. **Extract**:
   - Unzip to: `C:\ffmpeg\`
   - Should have: `C:\ffmpeg\bin\ffmpeg.exe`

3. **Add to PATH**:
   ```powershell
   # Open System Environment Variables
   # Start → "Edit system environment variables"
   # Advanced → Environment Variables
   # System Variables → Path → New
   # Add: C:\ffmpeg\bin
   ```

4. **Verify** (restart terminal first):
   ```powershell
   ffmpeg -version
   ```

### **macOS:**
```bash
# Install via Homebrew
brew install ffmpeg

# Verify
ffmpeg -version
```

---

## 🧪 **Validate Installation**

```bash
# Run sanity check
python tests/test_ffmpeg.py

# Expected output:
# ✅ FFmpeg found
# ✅ Test video created
# ✅ Metadata extracted
# ✅ Audio extracted
# ✅ Merge successful
```

---

## 💻 **Usage in Code**

### **Basic Usage:**
```python
from pathlib import Path
from src.core.ffmpeg_service import FFmpegService

# Initialize (fails if FFmpeg not installed)
service = FFmpegService()

# Get video info
metadata = service.get_video_metadata(Path("video.mp4"))
print(f"Duration: {metadata['duration']}s")
print(f"Resolution: {metadata['width']}x{metadata['height']}")

# Extract audio
service.extract_audio(
    input_path=Path("video.mp4"),
    output_path=Path("audio.mp3")
)

# Merge video + audio
service.merge_video_audio(
    video_path=Path("silent_video.mp4"),
    audio_path=Path("narration.mp3"),
    output_path=Path("final.mp4")
)
```

### **Integration with OmniComni Pipeline:**
```python
from src.core.ffmpeg_service import FFmpegService

# After generating videos and audio
service = FFmpegService()

# Merge scene video with narration
for scene_id in range(1, 7):
    service.merge_video_audio(
        video_path=Path(f"output/video/clips/topic/scene_{scene_id:02d}.mp4"),
        audio_path=Path(f"output/{timestamp}_topic/2_audio/scene_{scene_id:02d}_audio.mp3"),
        output_path=Path(f"output/final/scene_{scene_id:02d}_final.mp4")
    )
```

---

## 🎯 **Complete Workflow Update**

```bash
# 1. Generate scenes + audio
python pipeline_manager.py --topic "Cyberpunk Tokyo"

# 2. Generate images
python generate_images.py --input output/{timestamp}_cyberpunk_tokyo/1_scripts/cyberpunk_tokyo_scenes.json

# 3. Generate videos
python generate_videos.py --topic cyberpunk_tokyo_scenes

# 4. Merge video + audio (NEW!)
python merge_assets.py --topic cyberpunk_tokyo_scenes

# Result: Complete videos with synchronized audio!
```

---

## 🔧 **Advanced: FFmpeg Commands**

The service wraps these common FFmpeg operations:

### **Extract Audio:**
```bash
ffmpeg -i video.mp4 -vn -acodec libmp3lame -ab 192k audio.mp3
```

### **Merge Video + Audio:**
```bash
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4
```

### **Get Video Info:**
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of json video.mp4
```

---

## ⚠️ **Troubleshooting**

### **"FFmpeg binary not found in PATH"**
```bash
# Check if installed
which ffmpeg  # Linux/Mac
where ffmpeg  # Windows

# If not found, install per instructions above
```

### **"command not found: ffmpeg"**
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Add to PATH and restart terminal
- **macOS**: `brew install ffmpeg`

### **Windows PATH not working**
1. Restart terminal after adding to PATH
2. Verify: `echo %PATH%` should include ffmpeg folder
3. Try system-wide PATH (not user PATH)

---

## 📋 **Dependencies**

**Updated requirements.txt:**
```
# FFmpeg (binary must be installed separately)
# No Python package needed - uses subprocess
```

**Binary Requirements:**
- FFmpeg 4.x or 5.x+
- Must be in system PATH
- Includes ffprobe (comes with FFmpeg)

---

## ✅ **Follows OmniComni Patterns**

✅ Located in `src/core/` (matches our architecture)  
✅ Uses custom `ConfigurationError` exception  
✅ Fail-fast validation (on init)  
✅ Comprehensive logging  
✅ Type hints and docstrings  
✅ pathlib for all paths  

**Ready for Task 11: Final Assembly!** 🎬
