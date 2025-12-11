# OmniComni - AI Audio/Video Scene Generation Pipeline

Complete pipeline for generating audio scenes and video storyboards using AI.

## 🚀 Quick Start

### Audio Pipeline (Topic → Scenes → MP3s)
```bash
python main_audio.py "A detective solving a mystery"
```

### Video Pipeline (Topic → Storyboard → Audio)
```bash
# Generate scene storyboard
python main_video.py "Cyberpunk Tokyo" 0.5

# Generate audio narration
python generate_audio.py --input project_folder/1_scripts/cyberpunk_tokyo_scenes.json
```

## 📁 Project Structure

```
omnicomni/
├── src/
│   ├── audio/              # Audio pipeline modules
│   └── video/              # Video pipeline modules
├── tests/                  # Test suite
├── experiments/            # Experimental code
├── docs/                   # Documentation
├── main_audio.py          # Audio CLI
├── main_video.py          # Video scene generation CLI
├── generate_audio.py      # Video audio generation CLI
└── requirements.txt
```

## 🎯 Features

### Audio Pipeline
- ✅ AI scene generation (Llama-3.2-3B)
- ✅ Emotion-based voice selection
- ✅ edge-tts audio synthesis
- ✅ Multi-GPU support

### Video Pipeline  
- ✅ Stable Diffusion-optimized scene descriptions
- ✅ AI narration generation
- ✅ Async audio processing
- ✅ Configurable voices

### Professional Setup
- ✅ Windows + Linux support
- ✅ CUDA optimization
- ✅ Comprehensive troubleshooting
- ✅ 25 GPU test cases

## 📚 Documentation

- **[SETUP.md](docs/SETUP.md)** - Complete environment setup
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and fixes
- **[TASK3_AUDIO_ENGINE.md](docs/TASK3_AUDIO_ENGINE.md)** - Audio generation guide
- **[STRUCTURE.md](STRUCTURE.md)** - Project organization

## 🧪 Testing

```bash
# GPU test suite (25 tests)
python tests/test_gpu_extreme.py

# Model verification
python tests/verify_setup.py
```

## 💡 Requirements

- Python 3.10+
- NVIDIA GPU (8GB+ VRAM recommended)
- CUDA 11.8 or 12.1
- Dependencies: `pip install -r requirements.txt`

## 📄 License

See LICENSE file for details.

# example useage
# 1️⃣ Generate Scenes + Audio (~30 seconds)
python pipeline_manager.py --topic "Northern Lights Adventure"

# 2️⃣ Generate Images (~60 seconds)
# (Copy the exact path from step 1 output)
python generate_images.py --input output/20241210_XXXXXX_northern_lights_adventure/1_scripts/northern_lights_adventure_scenes.json

# 3️⃣ Generate Videos (~5 minutes)
python generate_videos.py --topic northern_lights_adventure_scenes

# 4️⃣ Merge Video + Audio (~2 minutes)
python merge_scenes.py --topic northern_lights_adventure_scenes

# 5️⃣ Create Final Video (~3 minutes)
python concat_scenes.py --topic northern_lights_adventure_scenes

# 🎉 RESULT: Complete polished video ready for distribution!
