# Project Reorganization Plan

## New Clean Structure

```
omnicomni/
├── src/                          # Core modules
│   ├── scene_generator.py        # AI scene generation (Llama-3.2-3B-Instruct)
│   ├── audio_generator.py        # Audio synthesis (edge-tts)
│   └── utils.py                  # Helper functions
├── main.py                       # Main pipeline entry point
├── config.py                     # Configuration settings
├── requirements.txt              # Dependencies
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
└── output/                       # Generated projects (gitignored)
```

## Files to Keep (Updated)
- ✅ scene_generator_improved.py → src/scene_generator.py
- ✅ audio_generator.py → src/audio_generator.py
- ✅ Create new main.py (combined pipeline)
- ✅ Create config.py
- ✅ Update requirements.txt
- ✅ Rewrite README.md
- ✅ Create QUICKSTART.md

## Files to Archive/Remove
- ❌ pipeline.py (old version)
- ❌ scene_generator_open.py (didn't work)
- ❌ scene_generator_flex.py (didn't work)
- ❌ scene_generator_phi.py (not needed)
- ❌ demo.py (keep for reference but move to examples/)
- ❌ test_audio.py (move to examples/)
- ❌ authenticate.py (not needed)
- ❌ setup_check.py (move to utils/)
