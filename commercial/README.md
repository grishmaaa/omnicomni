# 🎬 Commercial AI Video Generator

**Production-ready video generation pipeline using commercial APIs**

Generate professional videos in minutes using:
- 🧠 **Groq** (Llama-3.3) for story generation
- 🎨 **Fal.ai FLUX** for photorealistic images
- 🎬 **Fal.ai Minimax** for smooth video animation
- 🎙️ **ElevenLabs** for professional voiceovers
- 📱 **TikTok optimization** built-in

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.commercial.txt
```

### 2. Set Up API Keys

Copy the example environment file:
```bash
cp .env.commercial.example .env.commercial
```

Edit `.env.commercial` and add your API keys:
```bash
GROQ_API_KEY=gsk_your_key_here
FAL_API_KEY=your_fal_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**Get your API keys:**
- **Groq:** https://console.groq.com
- **Fal.ai:** https://fal.ai/dashboard
- **ElevenLabs:** https://elevenlabs.io/app/settings

### 3. Run the Streamlit UI

```bash
cd commercial/ui
python run.py
```

Open your browser to **http://localhost:8502**

---

## 💰 Cost Breakdown

| Service | Usage | Cost per Video |
|---------|-------|----------------|
| Groq (Story) | ~2K tokens | $0.002 |
| Fal.ai (Images) | 5 images @ 28 steps | $0.15 |
| Fal.ai (Videos) | 5 videos @ 5s | $0.50 |
| ElevenLabs (Voice) | ~500 characters | $0.15 |
| **Total** | | **~$0.82** |

**Recommended pricing:** $5-10 per video → **6-12x margin**

---

## 📁 Project Structure

```
commercial/
├── clients/              # API wrappers
│   ├── groq_client.py   # Story generation
│   ├── fal_client.py    # Images & video
│   └── elevenlabs_client.py  # Voice synthesis
├── ui/                   # Streamlit interface
│   ├── app.py           # Main UI
│   ├── run.py           # Launcher script
│   └── components/      # UI components
├── utils/               # Utilities
│   ├── tiktok_optimizer.py  # 9:16 conversion
│   └── cost_tracker.py      # Cost analytics
├── pipeline.py          # Main orchestrator
└── config.py            # Configuration
```

---

## 🎨 Features

### **4-Tab Streamlit UI**

1. **🚀 Quick Generate**
   - Simple topic input
   - One-click generation
   - Real-time progress tracking
   - Video player & download

2. **🎨 Advanced Settings**
   - 5 style presets (Cinematic, Photorealistic, Anime, TikTok Viral, Minimalist)
   - 6 professional voices (Rachel, Adam, Bella, Antoni, Elli, Josh)
   - Quality & motion controls

3. **📁 Projects**
   - Save/load projects (coming soon)
   - Batch generation (coming soon)

4. **📊 Analytics**
   - Real-time cost tracking
   - Monthly budget monitoring
   - Cost breakdown charts
   - Usage statistics

### **TikTok Optimization**

```python
from commercial.utils.tiktok_optimizer import TikTokOptimizer

optimizer = TikTokOptimizer()

# Convert to 9:16 vertical with captions
optimizer.optimize_video(
    input_path="video.mp4",
    output_path="tiktok_ready.mp4",
    add_captions=True,
    caption_text="🔥 Amazing AI Video!"
)

# Extract 3-second hook
optimizer.optimize_hook(
    video_path="video.mp4",
    output_path="hook.mp4",
    hook_duration=3.0
)
```

### **Cost Tracking**

```python
from commercial.utils.cost_tracker import CostTracker

tracker = CostTracker()

# Log costs
tracker.log_cost("groq", "story", 0.002)
tracker.log_cost("fal", "image", 0.15)

# Get totals
print(f"Total: ${tracker.get_total_cost():.2f}")
print(f"Today: ${tracker.get_daily_cost():.2f}")

# Check budget
status = tracker.check_budget(monthly_budget=100.0)
if status["alert"]:
    print("⚠️ Approaching budget limit!")

# Export report
tracker.export_csv("cost_report.csv")
```

---

## 🔧 Programmatic Usage

```python
from commercial.pipeline import CommercialPipeline
import os

# Initialize pipeline
pipeline = CommercialPipeline(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    fal_api_key=os.getenv("FAL_API_KEY"),
    elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")
)

# Generate video
result = pipeline.generate_video(
    topic="Cyberpunk Tokyo at night",
    style="cinematic",
    voice="rachel",
    aspect_ratio="16:9"  # or "9:16" for TikTok
)

print(f"✅ Video: {result['final_video']}")
print(f"💰 Cost: ${result['total_cost']:.2f}")
```

---

## 🎯 Use Cases

### **TikTok Creators**
- Generate viral content at scale
- Consistent brand voice
- Auto-captions for accessibility
- Cost: ~$0.82/video vs $50+ for freelancers

### **Commercial Clients**
- Product demos
- Brand storytelling
- Social media ads
- Full commercial rights

### **Content Agencies**
- Batch generation for clients
- Multiple style presets
- Cost tracking per project
- 10-50x ROI potential

---

## 🛠️ Advanced Configuration

### Custom Styles

Edit `commercial/ui/components/style_selector.py`:

```python
STYLE_PRESETS = {
    "my_style": {
        "name": "🌟 My Style",
        "description": "Custom style description",
        "keywords": "custom, keywords, here",
        "example": "Use case description"
    }
}
```

### Custom Voices

Add to `commercial/ui/components/voice_selector.py`:

```python
VOICE_LIBRARY = {
    "custom_voice": {
        "name": "Custom Voice",
        "gender": "Female",
        "accent": "British",
        "description": "Voice description",
        "use_case": "Best for..."
    }
}
```

---

## 📊 Monitoring & Analytics

### Real-Time Cost Tracking

The UI automatically tracks:
- Cost per video
- Monthly usage
- Budget alerts (at 80% and 90%)
- Service breakdown (Groq, Fal.ai, ElevenLabs)

### Export Reports

```python
from commercial.utils.cost_tracker import CostTracker

tracker = CostTracker()
tracker.export_csv("monthly_report.csv")
```

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'commercial'"

Use the launcher script:
```bash
cd commercial/ui
python run.py
```

### "Organization has been restricted" (Groq)

- Contact Groq support
- Or use alternative LLM (OpenAI, Together.ai)

### "API key not found"

Make sure `.env.commercial` exists and contains valid keys:
```bash
cat .env.commercial  # Linux/Mac
type .env.commercial  # Windows
```

---

## 📚 API Documentation

### Pipeline Methods

- `generate_video(topic, style, voice, aspect_ratio)` - Generate complete video
- `get_total_cost()` - Get cumulative cost
- `reset_usage()` - Reset cost counters

### TikTok Optimizer Methods

- `optimize_video(input, output, add_captions)` - Convert to 9:16
- `optimize_hook(video, output, duration)` - Extract hook

### Cost Tracker Methods

- `log_cost(service, operation, cost)` - Log cost entry
- `get_total_cost(service, since)` - Get filtered total
- `check_budget(monthly_budget)` - Check budget status
- `export_csv(output_path)` - Export report

---

## 🔐 Security

- API keys stored in `.env.commercial` (gitignored)
- No keys hardcoded in source
- Cost limits configurable

---

## 📝 License

This is a commercial pipeline. Ensure you have proper licenses for:
- Groq API usage
- Fal.ai commercial use
- ElevenLabs commercial voice rights

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API provider documentation
3. Check cost tracker for budget issues

---

## 🎓 Next Steps

1. **Get API keys** from all three providers
2. **Run the UI** and explore the interface
3. **Generate a test video** (costs ~$0.82)
4. **Optimize for TikTok** if needed
5. **Track costs** and adjust budget

**Ready to generate professional videos at scale!** 🚀
