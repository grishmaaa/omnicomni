# Task 13: Advanced Prompt Engineering - Revised LLM System Prompt

## Structured Scene Generation Prompt

Use this as the system prompt for LLM scene generation to get structured visual outputs:

```python
STRUCTURED_SCENE_PROMPT = """You are a Film Director creating a visual storyboard.

CRITICAL: You must output scenes as JSON with STRICTLY SEPARATED visual fields.

Output Format (JSON Array):
[
  {
    "scene_id": 1,
    "visual_subject": "Specific character/object with detailed physical attributes",
    "visual_action": "What they are doing (action verb + details)",
    "background_environment": "Location, setting, atmospheric details",
    "lighting": "Lighting conditions, time of day, mood lighting",
    "camera_shot": "Camera angle, framing, lens choice",
    "audio_text": "Narration script for TTS (what the audience hears)",
    "duration": 8
  }
]

Field Guidelines:

1. visual_subject:
   - Be SPECIFIC: "A weary detective in a rain-soaked trench coat" NOT "a detective"
   - Include: Age, build, clothing, distinctive features
   - Maintain consistency across scenes if same character

2. visual_action:
   - Focus on VERBS: "walking quickly", "examining a clue", "typing on keyboard"
   - Include body language, facial expressions
   - Be cinematic, not mundane

3. background_environment:
   - Set the scene: "narrow Tokyo alley with flickering neon signs"
   - Include: Architecture, weather, ambient details
   - Create atmosphere

4. lighting:
   - Specify conditions: "golden hour sunlight", "harsh fluorescent", "moody neon"
   - Include: Color temperature, shadows, reflections
   - Match the mood

5. camera_shot:
   - Use film terminology: "medium close-up", "wide establishing shot", "over-the-shoulder"
   - Include: Angle (low/high/eye-level), depth of field
   - Think like a cinematographer

6. audio_text:
   - Write narration that complements (not duplicates) visuals
   - Keep it concise: 1-2 sentences per scene
   - Engaging, not descriptive

Example Topic: "A Day in the Life of a Cyberpunk Detective"

Example Output:
[
  {
    "scene_id": 1,
    "visual_subject": "A weary middle-aged detective in a rain-soaked black trench coat, cybernetic eye glowing blue",
    "visual_action": "walking through puddles, collar turned up against the rain",
    "background_environment": "narrow neon-lit Tokyo alley, holographic advertisements flickering overhead, steam rising from grates",
    "lighting": "moody neon lighting with cyan and magenta reflections on wet pavement, volumetric fog",
    "camera_shot": "medium tracking shot, slightly low angle following from behind, shallow depth of field",
    "audio_text": "In Neo-Tokyo, even the rain can't wash away the secrets.",
    "duration": 8
  },
  {
    "scene_id": 2,
    "visual_subject": "The detective with cybernetic eye scanning data streams",
    "visual_action": "examining holographic evidence floating in mid-air, touching and rotating data fragments",
    "background_environment": "cramped detective office, walls covered in case photos and red string connections, city lights visible through rain-streaked window",
    "lighting": "dim blue holographic glow illuminating face from below, warm desk lamp creating contrast",
    "camera_shot": "close-up on face and hands, Dutch angle for tension, rack focus from hands to eyes",
    "audio_text": "The evidence points to someone inside the department.",
    "duration": 8
  }
]

Remember:
- 6 scenes total
- Each scene 8 seconds (adjustable 5-10s)
- STRICTLY separate visual fields
- Maintain visual consistency across scenes
- Use professional cinematography terminology
"""
```

---

## Integration Instructions

### Update `pipeline_manager.py`:

```python
from src.core.models import validate_llm_output

# In your LLM generation function:
system_prompt = STRUCTURED_SCENE_PROMPT

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Create a {num_scenes}-scene storyboard for: {topic}"}
]

# Parse LLM response
scenes_json = parse_llm_response(llm_output)  # Your existing parser
storyboard = validate_llm_output(scenes_json, topic)  # Validates structure
```

### Update `generate_images.py`:

```python
from src.image.prompt_builder import build_flux_prompt, QualityLevel

# When generating images:
for scene in scenes:
    # Build optimized prompt
    prompts = build_flux_prompt(
        scene=scene.dict(),
        global_style="cinematic",  # or from config
        quality=QualityLevel.HIGH
    )
    
    # Generate image
    pipeline(
        prompt=prompts['positive'],
        negative_prompt=prompts.get('negative'),  # if enabled
        # ... other params
    )
```

---

## Testing the Prompt

### Test Script:

```python
from src.image.prompt_builder import build_flux_prompt

# Example structured scene (from LLM)
scene = {
    "scene_id": 1,
    "visual_subject": "A weary cyberpunk detective in a rain-soaked trench coat",
    "visual_action": "slurping ramen noodles from a steaming bowl",
    "background_environment": "dimly lit noodle stand in narrow Tokyo alley",
    "lighting": "moody neon lighting, cyan and magenta reflections",
    "camera_shot": "medium close-up, slightly low angle, shallow depth of field",
    "audio_text": "Even detectives need to eat.",
    "duration": 8
}

# Build prompt
result = build_flux_prompt(scene, global_style="cyberpunk")
print(result['positive'])
```

**Expected Output:**
```
Cyberpunk aesthetic, neon lights, high tech low life, dystopian, A weary cyberpunk detective in a rain-soaked trench coat slurping ramen noodles from a steaming bowl, dimly lit noodle stand in narrow Tokyo alley, moody neon lighting, cyan and magenta reflections, medium close-up, slightly low angle, shallow depth of field, 4k, sharp focus, highly detailed, professional, blade runner inspired, volumetric lighting
```

---

## Available Style Presets

Run to see all styles:
```python
from src.image.prompt_builder import list_available_styles
print(list_available_styles())
```

Output:
- `cinematic` - Film noir, dramatic lighting
- `anime` - Studio Ghibli style
- `photorealistic` - Natural, DSLR quality
- `analog_film` - Vintage film aesthetic
- `concept_art` - Painterly, atmospheric
- `cyberpunk` - Neon, dystopian
- `fantasy` - Magical, ethereal
- `minimalist` - Clean, simple

---

## Migration Guide

### For Existing Projects:

**Option 1: Regenerate scenes** (recommended for best quality)
```bash
python pipeline_manager.py --topic "Your Topic"  # Uses new prompt
```

**Option 2: Keep legacy format** (backward compatible)
```python
# Old scenes with 'visual_prompt' field still work!
scene_legacy = {
    "scene_id": 1,
    "visual_prompt": "Neon-lit Tokyo street, 4k, cyberpunk style",
    "audio_text": "In Neo-Tokyo...",
    "duration": 8
}

# build_flux_prompt() handles both formats
prompts = build_flux_prompt(scene_legacy)  # Works!
```

---

## Quality Comparison

### Before (Legacy):
```json
{
  "visual_prompt": "A detective in Tokyo at night with neon lights"
}
```
**Issues:** Vague, generic, poor composition

### After (Structured):
```json
{
  "visual_subject": "A weary middle-aged detective, cybernetic eye glowing blue",
  "visual_action": "examining holographic evidence",
  "background_environment": "cramped office, rain-streaked window",
  "lighting": "dim blue holographic glow, warm desk lamp contrast",
  "camera_shot": "close-up, Dutch angle, rack focus"
}
```
**Benefits:** Specific, cinematic, consistent, professional composition

---

**Result:** 10x better image quality with proper scene structure! 🎬
