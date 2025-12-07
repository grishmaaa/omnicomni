"""
Improved Scene Generator - Better Prompting for Valid JSON
Uses Llama-3.2-3B-Instruct for better instruction following
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Any
import re


class ImprovedSceneGenerator:
    def __init__(self, model_name: str = "meta-llama/Llama-3.2-3B-Instruct"):
        """Initialize with Instruct model for better JSON generation"""
        print(f"Loading model: {model_name}")
        
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=quantization_config,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        print("Model loaded successfully!")
    
    def get_director_prompt(self, topic: str) -> str:
        """Create improved prompt for JSON generation"""
        # Using chat format for Instruct models
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a JSON generator for audio drama scenes. You must output ONLY valid JSON, nothing else.<|eot_id|><|start_header_id|>user<|end_header_id|>

Create 5 engaging audio drama scenes about: {topic}

Output a JSON array with exactly this structure:
[
  {{"scene_number": 1, "speaker": "Narrator", "text": "Opening scene text here.", "emotion": "mysterious"}},
  {{"scene_number": 2, "speaker": "Character Name", "text": "Dialogue here.", "emotion": "excited"}},
  {{"scene_number": 3, "speaker": "Another Character", "text": "More dialogue.", "emotion": "serious"}},
  {{"scene_number": 4, "speaker": "Character", "text": "Continuing the story.", "emotion": "dramatic"}},
  {{"scene_number": 5, "speaker": "Narrator", "text": "Closing scene.", "emotion": "mysterious"}}
]

Rules:
- Output ONLY the JSON array, no other text
- Each scene must have: scene_number, speaker, text, emotion
- text: 1-3 sentences of dialogue/narration
- emotion: must be one of: mysterious, excited, serious, dramatic, neutral
- Create a narrative arc relevant to the topic

JSON:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""
        return prompt
    
    def generate_scenes(self, topic: str, max_new_tokens: int = 1200, temperature: float = 0.7) -> List[Dict[str, Any]]:
        """Generate scenes with improved parsing"""
        print(f"\n{'='*60}")
        print(f"Generating scenes for topic: {topic}")
        print(f"{'='*60}\n")
        
        prompt = self.get_director_prompt(topic)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        print("Generating with Llama-3.2-3B-Instruct...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Debug: show what was generated
        print("\n" + "="*60)
        print("RAW GENERATED TEXT (for debugging):")
        print("="*60)
        # Show last 500 chars (where JSON should be)
        print(generated_text[-800:])
        print("="*60 + "\n")
        
        # Extract JSON
        scenes = self._extract_json_scenes(generated_text)
        
        print(f"\n✓ Generated {len(scenes)} scenes")
        return scenes
    
    def _extract_json_scenes(self, text: str) -> List[Dict[str, Any]]:
        """Improved JSON extraction"""
        # Try to find JSON array
        json_start = text.rfind('[')  # Use rfind to get the LAST occurrence
        json_end = text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0 or json_start >= json_end:
            print("Warning: No JSON array found")
            return self._create_fallback_scenes()
        
        json_str = text[json_start:json_end]
        
        print(f"\nExtracted JSON string (length: {len(json_str)} chars):")
        print(json_str[:300] + "..." if len(json_str) > 300 else json_str)
        
        try:
            scenes = json.loads(json_str)
            
            if not isinstance(scenes, list):
                raise ValueError("JSON is not a list")
            
            # Validate and clean scenes
            required_fields = {"scene_number", "speaker", "text", "emotion"}
            valid_scenes = []
            
            for scene in scenes:
                if isinstance(scene, dict) and all(field in scene for field in required_fields):
                    valid_scenes.append(scene)
            
            if len(valid_scenes) > 0:
                print(f"✓ Successfully parsed {len(valid_scenes)} valid scenes!")
                return valid_scenes
            else:
                raise ValueError("No valid scenes found")
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Attempting to fix JSON...")
            
            # Try common fixes
            json_str = json_str.replace("'", '"')  # Single to double quotes
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
            json_str = re.sub(r'}\s*{', '},{', json_str)  # Add missing commas between objects
            
            try:
                scenes = json.loads(json_str)
                if isinstance(scenes, list) and len(scenes) > 0:
                    print("✓ Fixed and parsed JSON!")
                    return scenes
            except:
                pass
            
            print("Could not parse JSON, using fallback scenes")
            return self._create_fallback_scenes()
    
    def _create_fallback_scenes(self) -> List[Dict[str, Any]]:
        """Fallback scenes"""
        return [
            {"scene_number": 1, "speaker": "Narrator", "text": "Welcome to this audio experience. Let's explore an interesting topic together.", "emotion": "neutral"},
            {"scene_number": 2, "speaker": "Host", "text": "Today we'll dive deep into the subject and uncover fascinating insights.", "emotion": "excited"},
            {"scene_number": 3, "speaker": "Narrator", "text": "Thank you for listening. Stay tuned for more engaging content.", "emotion": "neutral"}
        ]
    
    def save_scenes(self, scenes: List[Dict[str, Any]], output_file: str):
        """Save scenes to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Scenes saved to: {output_file}")


if __name__ == "__main__":
    generator = ImprovedSceneGenerator()
    
    topic = "A mysterious signal from deep space detected by scientists"
    scenes = generator.generate_scenes(topic)
    
    print("\n" + "="*60)
    print("GENERATED SCENES")
    print("="*60)
    for scene in scenes:
        print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
        print(f"  \"{scene['text']}\"")
    
    generator.save_scenes(scenes, "scenes_improved.json")
