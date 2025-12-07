# ⚡ Quick Start Guide

## Install & Run in 3 Steps

### 1️⃣ Install

```bash
pip install -r requirements.txt
```

### 2️⃣ Authenticate

```bash
huggingface-cli login
# Paste your token from: https://huggingface.co/settings/tokens
# Request model access: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct
```

### 3️⃣ Generate!

```bash
python main.py "A mysterious signal from deep space"
```

**Done!** 🎉 Your audio files are in `output/`

---

## Common Commands

```bash
# Basic
python main.py "Your topic"

# More scenes
python main.py "Your topic" --scenes 7

# Custom output
python main.py "Your topic" --output my_projects

# Debug mode
python main.py "Your topic" --verbose

# Just scenes, no audio
python main.py "Your topic" --no-audio
```

---

## What You Get

```
output/20251207_143022_your_topic/
├── scenes.json          # AI-generated scenes
├── summary.json         # Metadata
├── README.md           # Project summary
└── your_topic/         # Audio MP3 files
```

---

## Need Help?

- Full docs: See `README.md`
- Configuration: Edit `config.py`
- Issues: Check the Troubleshooting section in README

---

**That's it! Start creating audio dramas! 🎬**
