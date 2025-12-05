# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Authenticate with Hugging Face

The Llama-3.2-3B model requires Hugging Face authentication.

**First time setup:**

```bash
# Install huggingface-cli (if not already installed)
pip install huggingface-hub

# Login to Hugging Face
huggingface-cli login
```

When prompted, paste your token from: https://huggingface.co/settings/tokens

**Request model access:**
1. Visit: https://huggingface.co/meta-llama/Llama-3.2-3B
2. Click "Request Access" (approval is usually instant)

### Step 2: Verify Setup

```bash
python setup_check.py
```

This will check:
- ✓ All packages are installed
- ✓ edge-tts is working
- ✓ Hugging Face authentication is configured

### Step 3: Run the Pipeline

**Interactive mode:**
```bash
python pipeline.py
```

**Command line:**
```bash
python pipeline.py "Your topic here"
```

## 📝 Example Usage

```bash
# Mystery story
python pipeline.py "The discovery of a mysterious ancient artifact"

# Sci-fi
python pipeline.py "First contact with an alien civilization"

# Educational
python pipeline.py "How black holes work, explained simply"
```

## 📁 Output

Each run creates a timestamped folder:

```
output/
└── 20251130_145622_ancient_artifact/
    ├── scenes.json              # Scene definitions
    ├── summary.json             # Complete metadata
    ├── README.md               # Human-readable summary
    └── audio/                  # Audio files
        ├── ancient_artifact_scene01_narrator_mysterious.mp3
        ├── ancient_artifact_scene02_dr_chen_excited.mp3
        └── ancient_artifact_scene03_professor_serious.mp3
```

## 🎯 What Each Script Does

| Script | Purpose |
|--------|---------|
| `pipeline.py` | **Main script** - Run this to generate audio scenes |
| `scene_generator.py` | Generates JSON scenes using Llama-3.2-3B |
| `audio_generator.py` | Converts scenes to audio using edge-tts |
| `setup_check.py` | Verifies installation and authentication |

## 🔧 Troubleshooting

### "Access to model meta-llama/Llama-3.2-3B is restricted"

**Solution:**
1. Request access: https://huggingface.co/meta-llama/Llama-3.2-3B
2. Run: `huggingface-cli login`
3. Paste your token

### "CUDA out of memory"

**Solution:**
- The model uses 4-bit quantization (requires ~4GB GPU memory)
- Close other GPU applications
- If still failing, you may need a GPU with more memory

### "edge-tts not working"

**Solution:**
- Check internet connection (edge-tts requires online access)
- Run: `python setup_check.py` to test

### "No JSON found in output"

**Solution:**
- The model sometimes generates text before JSON
- The script has fallback scenes
- Try running again (AI generation can vary)

## 🎨 Customization

### Change Number of Scenes

Edit `scene_generator.py`, line ~35:
```python
Generate a JSON array of 3-5 scenes.  # Change to 5-7, etc.
```

### Change Voices

Edit `audio_generator.py`, line ~20:
```python
self.voice_map = {
    "neutral": "en-US-ChristopherNeural",
    "excited": "en-US-JennyNeural",
    # Add your custom voices
}
```

List available voices:
```python
python -c "import asyncio; import edge_tts; asyncio.run(edge_tts.list_voices())"
```

### Change Generation Parameters

Edit `scene_generator.py`, line ~90:
```python
scenes = generator.generate_scenes(
    topic,
    max_new_tokens=1024,  # Increase for longer scenes
    temperature=0.7        # 0.1-1.0: lower = more focused
)
```

## 💡 Tips

1. **Be specific with topics** - More detail = better scenes
2. **Check scenes.json** - Review generated scenes before listening
3. **Experiment with temperature** - Higher values = more creative
4. **Organize projects** - Use `--output` flag for different folders

## 📚 Advanced Usage

### Use as Library

```python
from pipeline import AudioScenePipeline

# Create pipeline
pipeline = AudioScenePipeline(output_base_dir="my_output")

# Generate
results = pipeline.run("Your topic")

# Access results
print(f"Generated {results['num_scenes']} scenes")
print(f"Audio files: {results['audio_files']}")
```

### Generate Only Scenes

```python
from scene_generator import SceneGenerator

generator = SceneGenerator()
scenes = generator.generate_scenes("Your topic")
generator.save_scenes(scenes, "my_scenes.json")
```

### Generate Only Audio

```python
from audio_generator import AudioGenerator
import json

# Load scenes
with open("scenes.json") as f:
    scenes = json.load(f)

# Generate audio
generator = AudioGenerator()
audio_files = generator.generate_audio_sync(scenes, "my_topic")
```

## 🎬 Workflow

```
Topic Input
    ↓
[Llama-3.2-3B] → Generate Scenes (JSON)
    ↓
[edge-tts] → Generate Audio Files
    ↓
Organized Output Folder
```

## 📦 File Structure

```
omnicomnimodel/
├── pipeline.py              # Main orchestrator
├── scene_generator.py       # AI scene generation
├── audio_generator.py       # Text-to-speech
├── setup_check.py          # Setup verification
├── requirements.txt        # Dependencies
├── README.md              # Full documentation
├── QUICKSTART.md          # This file
└── output/                # Generated projects
    └── [timestamp_topic]/
        ├── scenes.json
        ├── summary.json
        ├── README.md
        └── audio/
```

## ⚡ Quick Commands

```bash
# Setup
pip install -r requirements.txt
huggingface-cli login
python setup_check.py

# Run
python pipeline.py "Your topic"

# Help
python pipeline.py --help
```

## 🎯 Next Steps

After your first successful run:

1. ✅ Check the output folder
2. ✅ Listen to the generated audio files
3. ✅ Review scenes.json to see what was generated
4. ✅ Try different topics
5. ✅ Experiment with customizations

---

**Need help?** Check the full README.md for detailed documentation.
