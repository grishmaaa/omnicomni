# 🎬 OmniComni - AI Audio Scene Generator

Generate engaging audio dramas from any topic using AI scene generation and text-to-speech synthesis.

## ✨ Features

- 🤖 **AI Scene Generation**: Uses Llama-3.2-3B-Instruct for creative, topic-relevant scenes
- 🎭 **Smart Voice Selection**: Automatically selects voices based on emotion and character
- 🎵 **High-Quality Audio**: Multiple natural voices via Microsoft Edge TTS
- 📁 **Organized Output**: Timestamped projects with scenes, audio, and metadata
- 🚀 **Multi-GPU Support**: Efficiently uses 4-bit quantization and multi-GPU setups

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Authentication

```bash
# Login to HuggingFace (required for Llama models)
huggingface-cli login

# Request model access at:
# https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
```

### Generate Your First Audio Drama

```bash
python main.py "A mysterious signal from deep space"
```

That's it! Your audio scenes will be in `output/TIMESTAMP_topic/`

## 📖 Usage

### Basic

```bash
python main.py "Your topic here"
```

### Advanced Options

```bash
# Generate 7 scenes instead of default 5
python main.py "Ancient mysteries of Egypt" --scenes 7

# Use custom output directory
python main.py "Space exploration" --output my_projects

# Show debug information
python main.py "Detective story" --verbose

# Generate scenes only (no audio)
python main.py "Your topic" --no-audio
```

### Full Options

```bash
python main.py --help
```

## 📁 Output Structure

Each run creates a timestamped project folder:

```
output/
└── 20251207_143022_mysterious_signal/
    ├── scenes.json              # AI-generated scenes
    ├── summary.json             # Complete metadata
    ├── README.md               # Human-readable summary
    └── mysterious_signal/       # Audio files
        ├── mysterious_signal_scene01_narrator_mysterious.mp3
        ├── mysterious_signal_scene02_dr_patel_excited.mp3
        └── ...
```

## 🎨 Available Emotions & Voices

| Emotion | Voice | Character Type |
|---------|-------|----------------|
| `mysterious` | Guy (male) | Deep, enigmatic |
| `excited` | Jenny (female) | Enthusiastic, energetic |
| `serious` | Ryan (male, British) | Authoritative, formal |
| `dramatic` | Aria (female) | Expressive, theatrical |
| `neutral` | Christopher (male) | Clear, balanced |

## ⚙️ Configuration

Edit `config.py` to customize:

- Model selection
- Number of scenes
- Temperature and creativity settings
- Voice mappings
- Output directories

## 🖥️ Multi-GPU Usage

The pipeline automatically uses all available GPUs with `device_map="auto"`.

### Run Multiple Topics in Parallel

```bash
# Run 4 different topics simultaneously
CUDA_VISIBLE_DEVICES=0 python main.py "Topic 1" &
CUDA_VISIBLE_DEVICES=1 python main.py "Topic 2" &
CUDA_VISIBLE_DEVICES=2 python main.py "Topic 3" &
CUDA_VISIBLE_DEVICES=3 python main.py "Topic 4" &
wait
```

## 📚 Project Structure

```
omnicomni/
├── src/
│   ├── scene_generator.py    # AI scene generation
│   ├── audio_generator.py    # Audio synthesis
│   └── utils.py              # Helper functions
├── main.py                   # Main entry point
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
└── output/                   # Generated projects
```

## 🛠️ Development

### Running Tests

```bash
# Test scene generation only
python -c "from src.scene_generator import SceneGenerator; sg = SceneGenerator(); scenes = sg.generate_scenes('Test topic'); print(scenes)"

# Test audio generation only
python -c "from src.audio_generator import AudioGenerator; ag = AudioGenerator(); ag.generate_audio_sync([{'scene_number':1,'speaker':'Test','text':'Hello world','emotion':'neutral'}], 'test')"
```

### Module Usage

```python
from src.scene_generator import SceneGenerator
from src.audio_generator import AudioGenerator

# Generate scenes
generator = SceneGenerator()
scenes = generator.generate_scenes("Your topic", num_scenes=5)

# Generate audio
audio_gen = AudioGenerator(output_dir="my_output")
audio_files = audio_gen.generate_audio_sync(scenes, "my_topic")
```

## 💡 Tips

1. **Be specific with topics** - More detail = better scenes
2. **Adjust temperature** - Higher (0.8-0.9) = more creative, Lower (0.5-0.6) = more focused
3. **Try different scene counts** - 3-7 works well for most topics
4. **Use verbose mode** - See what the AI generates for debugging

## 🐛 Troubleshooting

### Model Access Denied

Visit https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct and click "Request Access"

### CUDA Out of Memory

The model uses 4-bit quantization (~4GB). If still running out of memory:
- Close other GPU applications
- Use a smaller batch size

### Generic Fallback Scenes

This means the AI couldn't generate valid JSON. Enable verbose mode:
```bash
python main.py "Your topic" --verbose
```

This will show what the model generated so you can debug.

## 📝 License

This project uses:
- Llama-3.2-3B-Instruct (Meta's license)
- edge-tts (MIT License)
- transformers, torch (Apache 2.0)

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new voice options
- Improve prompts
- Add new features
- Fix bugs

---

**Version**: 1.0.0  
**Created by**: OmniComni Team
