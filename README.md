# Audio Scene Generation Pipeline

A complete AI-powered pipeline that generates audio dramas from topics using Llama-3.2-3B for scene generation and edge-tts for text-to-speech synthesis.

## Features

- 🤖 **AI Scene Generation**: Uses Llama-3.2-3B with 4-bit quantization for efficient scene creation
- 🎭 **Director Prompt**: Structured prompting for consistent JSON scene output
- 🔊 **Text-to-Speech**: Multiple voices with emotion-based voice selection
- 📁 **Organized Output**: Timestamped project folders with comprehensive metadata
- 🎯 **Proper Naming**: Consistent file naming conventions for easy management
- 🚀 **Easy to Use**: CLI and interactive modes

## Installation

```bash
pip install transformers bitsandbytes accelerate edge-tts torch
```

**Note**: You'll need a GPU with CUDA support for optimal performance. The model uses 4-bit quantization to reduce memory requirements.

## Quick Start

### Interactive Mode

```bash
python pipeline.py
```

Then enter your topic when prompted.

### Command Line Mode

```bash
python pipeline.py "The discovery of a mysterious ancient artifact"
```

### Advanced Options

```bash
# Custom output directory
python pipeline.py "A day in the life of an astronaut on Mars" --output my_projects

# Don't save scenes.json
python pipeline.py "The last library on Earth" --no-save-scenes
```

## How It Works

### 1. Scene Generation (`scene_generator.py`)

- Loads Llama-3.2-3B with 4-bit quantization
- Uses a carefully crafted "Director Prompt" to generate structured JSON scenes
- Each scene includes:
  - `scene_number`: Scene order (integer)
  - `speaker`: Character or narrator name
  - `text`: Dialogue or narration (1-3 sentences)
  - `emotion`: Emotional tone (neutral, excited, serious, mysterious, dramatic)

### 2. Audio Generation (`audio_generator.py`)

- Converts each scene to audio using edge-tts
- Selects appropriate voices based on emotion and speaker
- Generates files with naming convention: `{topic}_scene{XX}_{speaker}_{emotion}.mp3`
- Organizes files in topic-specific folders

### 3. Pipeline Orchestration (`pipeline.py`)

- Coordinates the entire workflow
- Creates timestamped project folders
- Generates comprehensive metadata and documentation
- Provides progress feedback

## Output Structure

Each run creates a timestamped project folder:

```
output/
└── 20251130_143022_ancient_artifact/
    ├── scenes.json              # Scene definitions
    ├── summary.json             # Complete metadata
    ├── README.md               # Human-readable summary
    └── audio/                  # Audio files
        ├── ancient_artifact_scene01_narrator_mysterious.mp3
        ├── ancient_artifact_scene02_dr_sarah_chen_excited.mp3
        └── ancient_artifact_scene03_professor_james_serious.mp3
```

## File Naming Convention

Audio files follow this pattern:
```
{topic_slug}_scene{number:02d}_{speaker}_{emotion}.mp3
```

Example:
```
ancient_artifact_scene01_narrator_mysterious.mp3
```

## Components

### `scene_generator.py`

Handles AI-powered scene generation:

```python
from scene_generator import SceneGenerator

generator = SceneGenerator()
scenes = generator.generate_scenes("Your topic here")
generator.save_scenes(scenes, "output.json")
```

### `audio_generator.py`

Handles text-to-speech conversion:

```python
from audio_generator import AudioGenerator

generator = AudioGenerator(output_dir="audio_output")
audio_files = generator.generate_audio_sync(scenes, topic="my_topic")
```

### `pipeline.py`

Complete end-to-end pipeline:

```python
from pipeline import AudioScenePipeline

pipeline = AudioScenePipeline(output_base_dir="output")
results = pipeline.run("Your topic here")
```

## Voice Selection

The system automatically selects voices based on emotion:

| Emotion     | Voice                    |
|-------------|--------------------------|
| neutral     | en-US-ChristopherNeural  |
| excited     | en-US-JennyNeural        |
| serious     | en-GB-RyanNeural         |
| mysterious  | en-US-GuyNeural          |
| dramatic    | en-US-AriaNeural         |

## Director Prompt

The director prompt is designed to generate consistent, high-quality scenes:

- Acts as a creative director for audio storytelling
- Requests 3-5 scenes with narrative arc
- Specifies exact JSON structure
- Emphasizes concise, engaging content
- Ensures audio-suitable formatting

## Debugging

### Common Issues

1. **CUDA Out of Memory**: The model uses 4-bit quantization, but if you still run out of memory, try:
   - Closing other GPU applications
   - Reducing `max_new_tokens` in scene generation

2. **JSON Parsing Errors**: The system includes fallback scenes if generation fails
   - Check the generated text output
   - Adjust temperature parameter for more consistent output

3. **Audio Generation Fails**: 
   - Ensure edge-tts is properly installed
   - Check internet connection (edge-tts requires online access)

### Verbose Output

All scripts include detailed progress output showing:
- Model loading status
- Scene generation progress
- Audio file creation
- File paths and statistics

## Customization

### Modify Voice Selection

Edit `audio_generator.py`:

```python
self.voice_map = {
    "neutral": "en-US-ChristopherNeural",
    "excited": "en-US-JennyNeural",
    # Add your custom mappings
}
```

### Adjust Scene Generation

Edit `scene_generator.py`:

```python
scenes = generator.generate_scenes(
    topic,
    max_new_tokens=1024,  # Increase for longer scenes
    temperature=0.7        # Higher = more creative
)
```

### Change Output Structure

Edit `pipeline.py` to customize folder structure and metadata.

## Requirements

- Python 3.8+
- CUDA-capable GPU (recommended)
- ~4GB GPU memory (with 4-bit quantization)
- Internet connection (for edge-tts)

## License

This project uses:
- Llama-3.2-3B (Meta's license)
- edge-tts (MIT License)
- transformers, bitsandbytes, accelerate (Apache 2.0)

## Examples

### Example 1: Mystery Story
```bash
python pipeline.py "The discovery of a mysterious ancient artifact in the Amazon"
```

### Example 2: Sci-Fi
```bash
python pipeline.py "First contact with an alien civilization"
```

### Example 3: Educational
```bash
python pipeline.py "How photosynthesis works, explained for children"
```

## Tips

1. **Be Specific**: More detailed topics generate better scenes
2. **Check Output**: Review `scenes.json` to see what was generated
3. **Iterate**: Run multiple times with different topics to see variety
4. **Organize**: Use the `--output` flag to organize different projects

## Troubleshooting

### Model Download

First run will download Llama-3.2-3B (~2GB). This may take time depending on your connection.

### Hugging Face Authentication

If you need access to gated models:

```bash
huggingface-cli login
```

## Contributing

Feel free to customize and extend:
- Add more voice options
- Implement different scene structures
- Add background music
- Create video from audio + images
- Add multi-language support

---

**Created by**: Audio Scene Pipeline
**Version**: 1.0.0
# omnicomni
