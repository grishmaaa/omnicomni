"""
Flexible Scene Generator - Tries Multiple Model Options
Automatically finds which Llama model you have access to
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Any, Optional
import re


class FlexibleSceneGenerator:
    # List of models to try in order of preference
    MODEL_OPTIONS = [
        "meta-llama/Llama-3.2-3B-Instruct",  # Instruct version
        "meta-llama/Llama-3.2-3B",           # Base version
        "meta-llama/Llama-3.2-1B-Instruct",  # Smaller instruct
        "meta-llama/Llama-3.2-1B",           # Smaller base
        "meta-llama/Llama-3.1-8B-Instruct",  # Older version
        "meta-llama/Meta-Llama-3-8B-Instruct", # Even older
    ]
    
    def __init__(self, preferred_model: Optional[str] = None):
        """Initialize with automatic model selection"""
        print("\n" + "="*70)
        print("FLEXIBLE MODEL LOADER")
        print("="*70)
        
        if preferred_model:
            models_to_try = [preferred_model] + self.MODEL_OPTIONS
        else:
            models_to_try = self.MODEL_OPTIONS
        
        self.model = None
        self.tokenizer = None
        self.model_name = None
        
        for model_name in models_to_try:
            print(f"\nTrying: {model_name}")
            if self._try_load_model(model_name):
                self.model_name = model_name
                print(f"\n✓ Successfully loaded: {model_name}")
                break
        
        if self.model is None:
            raise RuntimeError("Could not load any Llama model. Please check your access permissions.")
    
    def _try_load_model(self, model_name: str) -> bool:
        """Try to load a specific model"""
        try:
            print(f"  Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            print(f"  Loading model (16-bit, no quantization for compatibility)...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            self.tokenizer = tokenizer
            self.model = model
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "restricted" in error_msg.lower() or "authorized" in error_msg.lower():
                print(f"  ✗ Access denied")
            else:
                print(f"  ✗ Error: {error_msg[:100]}")
            return False
    
    def get_director_prompt(self, topic: str) -> str:
        """Create the director prompt"""
        prompt = f"""You are a creative director for audio storytelling. Create engaging scenes for an audio drama about: {topic}

Generate a JSON array of 3-5 scenes. Each scene must have:
- "scene_number": integer
- "speaker": string  
- "text": string (1-3 sentences)
- "emotion": string (neutral, excited, serious, mysterious, or dramatic)

Output ONLY valid JSON:

[
  {{
    "scene_number": 1,
    "speaker": "Narrator",
    "text": "Opening line here.",
    "emotion": "mysterious"
  }}
]

JSON Output:"""
        return prompt
    
    def generate_scenes(self, topic: str, max_new_tokens: int = 1024, temperature: float = 0.7) -> List[Dict[str, Any]]:
        """Generate scenes"""
        print(f"\n{'='*60}")
        print(f"Generating scenes for: {topic}")
        print(f"Using model: {self.model_name}")
        print(f"{'='*60}\n")
        
        prompt = self.get_director_prompt(topic)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        print("Generating with AI...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON
        scenes = self._extract_json_scenes(generated_text)
        
        print(f"\n✓ Generated {len(scenes)} scenes")
        return scenes
    
    def _extract_json_scenes(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON from generated text"""
        json_start = text.find('[')
        json_end = text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            print("Warning: No JSON found, using fallback")
            return self._create_fallback_scenes()
        
        json_str = text[json_start:json_end]
        
        try:
            scenes = json.loads(json_str)
            if not isinstance(scenes, list):
                raise ValueError("Not a list")
            
            required = {"scene_number", "speaker", "text", "emotion"}
            for scene in scenes:
                if not all(f in scene for f in required):
                    raise ValueError("Missing fields")
            
            return scenes
        except:
            print("JSON parsing failed, using fallback")
            return self._create_fallback_scenes()
    
    def _create_fallback_scenes(self) -> List[Dict[str, Any]]:
        """Fallback scenes"""
        return [
            {"scene_number": 1, "speaker": "Narrator", "text": "Welcome to this audio experience.", "emotion": "neutral"},
            {"scene_number": 2, "speaker": "Host", "text": "Let's explore this fascinating topic together.", "emotion": "excited"},
            {"scene_number": 3, "speaker": "Narrator", "text": "Thank you for listening.", "emotion": "neutral"}
        ]


if __name__ == "__main__":
    try:
        generator = FlexibleSceneGenerator()
        
        topic = "A mysterious signal from deep space"
        scenes = generator.generate_scenes(topic)
        
        print("\n" + "="*60)
        print("GENERATED SCENES")
        print("="*60)
        for scene in scenes:
            print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
            print(f"  \"{scene['text']}\"")
        
        # Save
        with open("scenes_flexible.json", 'w', encoding='utf-8') as f:
            json.dump(scenes, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Scenes saved to: scenes_flexible.json")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("1. Visit https://huggingface.co/meta-llama and request access to models")
        print("2. Ensure you're logged in: huggingface-cli whoami")
