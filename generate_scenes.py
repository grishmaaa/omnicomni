#!/usr/bin/env python3
"""
Director Engine - Video Scene Generation
Converts topics into structured JSON storyboards for video generation
Optimized for Stable Diffusion/Flux visual prompts
"""

import json
import re
import os
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import sys


# ============================================================================
# DIRECTOR SYSTEM PROMPT
# ============================================================================

DIRECTOR_SYSTEM_PROMPT = """You are a World-Class Film Director creating visual storyboards.

YOUR TASK: Convert the given topic into a cinematic story with detailed visual scenes.

CRITICAL RULES:
1. Output ONLY raw JSON. NO markdown formatting (no ```json), NO intro text, NO outro text.
2. Start directly with [ and end with ]
3. Each scene must be optimized for AI image generation (Stable Diffusion/Flux)

JSON SCHEMA (list of objects):
[
  {
    "scene_id": 1,
    "visual_prompt": "highly detailed description here",
    "audio_text": "Narration script (max 2 sentences)",
    "duration": 8
  }
]

VISUAL PROMPT REQUIREMENTS:
- Include: lighting type, camera angle, art style, quality markers
- Use keywords: "4k", "ultra detailed", "volumetric lighting", "cinematic"
- Specify: mood, colors, composition
- Be concrete and specific
- Maintain consistent visual style across all scenes

CREATIVE CONSTRAINTS:
- Create 4-6 scenes
- Total duration: 30-45 seconds (5-10s per scene)
- Follow narrative arc: beginning, middle, end
- Each scene must advance the story
- Visual style must be cohesive

OUTPUT FORMAT: Pure JSON only. Begin with [ and end with ]"""


# ============================================================================
# JSON CLEANING & VALIDATION
# ============================================================================

def clean_json_output(raw_text: str) -> str:
    """
    Aggressively clean LLM output to extract valid JSON
    Handles common failure modes: markdown blocks, conversational text
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', raw_text)
    text = re.sub(r'```\s*', '', text)
    
    # Find first [ and last ]
    start_idx = text.find('[')
    end_idx = text.rfind(']')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        raise ValueError("No valid JSON array found in output")
    
    # Extract just the JSON
    json_str = text[start_idx:end_idx + 1]
    
    return json_str


def validate_scenes(scenes: list) -> list:
    """
    Validate and fix scene structure
    Ensures all required fields exist
    """
    required_fields = {"scene_id", "visual_prompt", "audio_text", "duration"}
    validated = []
    
    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            print(f"⚠️  Warning: Scene {i} is not a dict, skipping")
            continue
        
        # Ensure all required fields exist
        fixed_scene = {
            "scene_id": scene.get("scene_id", i + 1),
            "visual_prompt": scene.get("visual_prompt", "A cinematic scene, 4k, detailed"),
            "audio_text": scene.get("audio_text", ""),
            "duration": scene.get("duration", 8)
        }
        
        # Validate types
        fixed_scene["scene_id"] = int(fixed_scene["scene_id"])
        fixed_scene["duration"] = int(fixed_scene["duration"])
        
        validated.append(fixed_scene)
    
    return validated


# ============================================================================
# FILENAME UTILITIES
# ============================================================================

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Convert any text into a safe filename
    Example: "Cats in Space!!!" -> "cats_in_space"
    """
    # Remove special characters
    safe = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    safe = re.sub(r'[\s]+', '_', safe)
    # Lowercase and trim
    safe = safe[:max_length].strip('_').lower()
    
    return safe or "untitled"


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_llama_model():
    """
    Load Llama-3.2-3B-Instruct with 4-bit quantization
    Reuses logic from test_llama.py
    """
    model_name = "meta-llama/Llama-3.2-3B-Instruct"
    
    print("📦 Loading Llama-3.2-3B-Instruct...")
    
    # Check CUDA
    if not torch.cuda.is_available():
        print("⚠️  WARNING: No GPU detected, loading on CPU (very slow)")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        return tokenizer, model, "cpu"
    
    # GPU available - use 4-bit quantization
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map={"": 0},  # Force GPU 0
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True
    )
    
    vram = torch.cuda.memory_allocated(0) / 1e9
    print(f"✅ Model loaded ({vram:.2f} GB VRAM)\n")
    
    return tokenizer, model, "cuda"


# ============================================================================
# SCENE GENERATION
# ============================================================================

def generate_scenes(
    topic: str,
    tokenizer,
    model,
    device: str,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> list:
    """
    Generate video scenes from topic using Llama model
    
    Args:
        topic: User topic (e.g., "Cyberpunk Tokyo")
        tokenizer: Loaded tokenizer
        model: Loaded model
        device: "cuda" or "cpu"
        temperature: 0.0-1.0 (lower = more deterministic)
        max_tokens: Maximum output length
    
    Returns:
        List of validated scene dicts
    """
    print(f"🎬 Generating scenes for: '{topic}'")
    print(f"   Temperature: {temperature}")
    
    # Create prompt
    user_prompt = f"Create a cinematic visual storyboard for: {topic}"
    
    full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{DIRECTOR_SYSTEM_PROMPT}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""
    
    # Tokenize
    inputs = tokenizer(full_prompt, return_tensors="pt")
    if device == "cuda":
        inputs = inputs.to(model.device)
    
    # Generate
    print("⚙️  Generating (this may take 30-60s)...")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True if temperature > 0 else False,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract just the assistant's response
    assistant_start = generated_text.rfind("[")
    if assistant_start != -1:
        raw_output = generated_text[assistant_start:]
    else:
        raw_output = generated_text
    
    print("✅ Generation complete\n")
    
    # Clean and parse
    try:
        cleaned = clean_json_output(raw_output)
        scenes = json.loads(cleaned)
        
        if not isinstance(scenes, list):
            raise ValueError("Output is not a list")
        
        validated = validate_scenes(scenes)
        
        print(f"✅ Parsed {len(validated)} scenes successfully\n")
        return validated
        
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"\n📄 Raw output (last 500 chars):")
        print(raw_output[-500:])
        print("\n💡 Try:")
        print("   - Lower temperature (0.3-0.5)")
        print("   - Run again (LLM output varies)")
        raise


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def save_scenes(scenes: list, topic: str, output_dir: str = "project_folder") -> str:
    """
    Save scenes to JSON file in organized structure
    Creates: project_folder/1_scripts/topic_scenes.json
    """
    # Create directory structure
    scripts_dir = Path(output_dir) / "1_scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename
    safe_topic = sanitize_filename(topic)
    filename = f"{safe_topic}_scenes.json"
    filepath = scripts_dir / filename
    
    # Save
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution"""
    print("\n" + "🎬" * 35)
    print(" " * 20 + "DIRECTOR ENGINE")
    print(" " * 15 + "Video Scene Generation")
    print("🎬" * 35 + "\n")
    
    # Get topic from command line
    if len(sys.argv) < 2:
        print("❌ Usage: python generate_scenes.py \"Your topic here\"")
        print("\nExample:")
        print("   python generate_scenes.py \"Cyberpunk Tokyo\"")
        print("   python generate_scenes.py \"The history of coffee\"")
        sys.exit(1)
    
    topic = sys.argv[1]
    
    # Optional: temperature override
    temperature = 0.7
    if len(sys.argv) > 2:
        try:
            temperature = float(sys.argv[2])
            print(f"🎚️  Using custom temperature: {temperature}")
        except:
            pass
    
    try:
        # Load model
        tokenizer, model, device = load_llama_model()
        
        # Generate scenes
        scenes = generate_scenes(topic, tokenizer, model, device, temperature)
        
        # Save to file
        filepath = save_scenes(scenes, topic)
        
        # Display results
        print("=" * 70)
        print("GENERATED SCENES")
        print("=" * 70 + "\n")
        
        total_duration = 0
        for scene in scenes:
            print(f"[Scene {scene['scene_id']}] ({scene['duration']}s)")
            print(f"  Visual: {scene['visual_prompt'][:80]}...")
            print(f"  Audio:  {scene['audio_text']}")
            print()
            total_duration += scene['duration']
        
        print("=" * 70)
        print(f"✅ SUCCESS!")
        print("=" * 70)
        print(f"\n📊 Total scenes: {len(scenes)}")
        print(f"⏱️  Total duration: {total_duration}s")
        print(f"💾 Saved to: {filepath}")
        print("\n" + "=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
