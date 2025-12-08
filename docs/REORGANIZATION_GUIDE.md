# Project Reorganization Guide

## Current Status
The reorganization script had conflicts with existing folders. Here's the manual approach:

## Step-by-Step Manual Reorganization

### 1. Create New Folders (if they don't exist)
```powershell
New-Item -ItemType Directory -Force -Path src/audio, src/video, tests, experiments, docs
```

### 2. Move Files

#### Audio Core → src/audio/
```powershell
# These are already in src/audio if they exist in src/
# If they exist in root, move them:
Move-Item -Force scene_generator.py src/audio/ -ErrorAction SilentlyContinue
Move-Item -Force audio_generator.py src/audio/ -ErrorAction SilentlyContinue
Move-Item -Force utils.py src/audio/ -ErrorAction SilentlyContinue
```

#### Video Core → src/video/
```powershell
Move-Item -Force generate_scenes.py src/video/scene_generator.py -ErrorAction SilentlyContinue
```

#### Tests → tests/
```powershell
Move-Item -Force test_llama.py tests/ -ErrorAction SilentlyContinue
Move-Item -Force test_gpu_extreme.py tests/ -ErrorAction SilentlyContinue
Move-Item -Force verify_setup.py tests/ -ErrorAction SilentlyContinue
```

#### Experiments → experiments/
```powershell
Move-Item -Force scene_generator_improved.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force scene_generator_flex.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force scene_generator_phi.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force scene_generator_open.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force pipeline_open.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force demo.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force authenticate.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force setup_check.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force test_audio.py experiments/ -ErrorAction SilentlyContinue
Move-Item -Force pipeline.py experiments/ -ErrorAction SilentlyContinue
```

#### Docs → docs/
```powershell
Move-Item -Force SETUP.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force TROUBLESHOOTING.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force QUICKSTART.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force MODEL_ACCESS.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force REORGANIZE.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force PROJECT_SUMMARY.md docs/ -ErrorAction SilentlyContinue
Move-Item -Force walkthrough.md docs/ -ErrorAction SilentlyContinue
```

### 3. Rename Main Entry Point
```powershell
# If main.py exists and main_audio.py doesn't
if (Test-Path "main.py" -and !(Test-Path "main_audio.py")) {
    Rename-Item main.py main_audio.py
}
```

### 4. Create main_video.py
Create file `main_video.py` with:
```python
#!/usr/bin/env python3
from src.video.scene_generator import main

if __name__ == "__main__":
    main()
```

### 5. Create __init__.py Files
```powershell
New-Item -ItemType File -Force -Path src/__init__.py
New-Item -ItemType File -Force -Path src/audio/__init__.py
New-Item -ItemType File -Force -Path src/video/__init__.py
```

### 6. Update Imports in main_audio.py
Change:
```python
from src.scene_generator import SceneGenerator
from src.audio_generator import AudioGenerator
```

To:
```python
from src.audio.scene_generator import SceneGenerator
from src.audio.audio_generator import AudioGenerator
```

## Final Structure
```
omnicomni/
├── src/
│   ├── audio/              # Audio pipeline
│   │   ├── __init__.py
│   │   ├── scene_generator.py
│   │   ├── audio_generator.py
│   │   └── utils.py
│   ├── video/              # Video pipeline
│   │   ├── __init__.py
│   │   └── scene_generator.py
│   └── __init__.py
├── tests/                  # All tests
│   ├── test_llama.py
│   ├── test_gpu_extreme.py
│   └── verify_setup.py
├── experiments/            # Old/experimental code
│   ├── scene_generator_*.py
│   ├── demo.py
│   └── ...
├── docs/                   # Documentation
│   ├── SETUP.md
│   ├── TROUBLESHOOTING.md
│   └── ...
├── output/                 # Generated outputs (gitignored)
├── main_audio.py          # Audio CLI entry point
├── main_video.py          # Video CLI entry point
├── config.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Usage After Reorganization

**Audio Pipeline:**
```bash
python main_audio.py "Your topic"
```

**Video Pipeline:**
```bash
python main_video.py "Your topic" 0.5
```

**Tests:**
```bash
python tests/test_llama.py
python tests/test_gpu_extreme.py
```
