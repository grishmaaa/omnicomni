"""
AI Scene Generator using Llama-3.2-3B-Instruct
Generates structured JSON scenes for audio dramas
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Any, Optional
import re
from pathlib import Path


class SceneGenerator:
    """Generates audio drama scenes using AI"""
    
    def __init__(self, model_name: str = "meta-llama/Llama-3.2-3B-Instruct", use_4bit: bool = True):
        """
        Initialize the scene generator
        
        Args:
            model_name: HuggingFace model identifier
            use_4bit: Use 4-bit quantization for memory efficiency
        """
        print(f"🤖 Loading AI model: {model_name}")
        
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load model with optional quantization
        if use_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16
            )
        
        print("✅ Model loaded successfully!\n")
    
    def generate_scenes(
        self, 
        topic: str, 
        num_scenes: int = 5,
        max_new_tokens: int = 1200, 
        temperature: float = 0.7,
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate scenes for a given topic
        
        Args:
            topic: The topic to generate scenes about
            num_scenes: Number of scenes to generate
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more creative)
            verbose: Show debug information
            
        Returns:
            List of scene dictionaries with scene_number, speaker, text, emotion
        """
        print(f"🎬 Generating {num_scenes} scenes for: {topic}")
        
        prompt = self._create_prompt(topic, num_scenes)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        print("⚙️  Running AI generation...")
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
        
        if verbose:
            print(f"\n{'='*60}")
            print("DEBUG: Generated text (last 800 chars)")
            print(f"{'='*60}")
            print(generated_text[-800:])
            print(f"{'='*60}\n")
        
        # Extract and parse JSON
        scenes = self._extract_json_scenes(generated_text, verbose)
        
        print(f"✅ Generated {len(scenes)} scenes successfully!\n")
        return scenes
    
    def _create_prompt(self, topic: str, num_scenes: int) -> str:
        """Create optimized prompt for JSON generation"""
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a JSON generator for audio drama scenes. Output ONLY valid JSON, nothing else.<|eot_id|><|start_header_id|>user<|end_header_id|>

Create {num_scenes} engaging audio drama scenes about: {topic}

Output a JSON array with exactly this structure:
[
  {{"scene_number": 1, "speaker": "Character Name", "text": "Dialogue or narration here.", "emotion": "mysterious"}},
  ...
]

Rules:
- Output ONLY the JSON array, no other text before or after
- Each scene: scene_number (int), speaker (string), text (1-3 sentences), emotion (string)
- emotion must be: mysterious, excited, serious, dramatic, or neutral
- Create a compelling narrative arc
- Make it relevant to the topic

JSON:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""
        return prompt
    
    def _extract_json_scenes(self, text: str, verbose: bool = False) -> List[Dict[str, Any]]:
        """Extract and validate JSON scenes from generated text"""
        # Find JSON array (use last occurrence to skip prompt)
        json_start = text.rfind('[')
        json_end = text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0 or json_start >= json_end:
            print("⚠️  Warning: No JSON found in output")
            return self._create_fallback_scenes()
        
        json_str = text[json_start:json_end]
        
        if verbose:
            print(f"Extracted JSON ({len(json_str)} chars):")
            print(json_str[:200] + "..." if len(json_str) > 200 else json_str)
        
        # Try parsing
        try:
            scenes = json.loads(json_str)
            
            if not isinstance(scenes, list):
                raise ValueError("Not a list")
            
            # Validate scenes
            valid_scenes = []
            required_fields = {"scene_number", "speaker", "text", "emotion"}
            
            for scene in scenes:
                if isinstance(scene, dict) and all(f in scene for f in required_fields):
                    valid_scenes.append(scene)
            
            if len(valid_scenes) > 0:
                return valid_scenes
            else:
                raise ValueError("No valid scenes")
                
        except (json.JSONDecodeError, ValueError) as e:
            if verbose:
                print(f"⚠️  JSON error: {e}")
                print("Attempting fixes...")
            
            # Try common fixes
            json_str = json_str.replace("'", '"')
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            json_str = re.sub(r'}\s*{', '},{', json_str)
            
            try:
                scenes = json.loads(json_str)
                if isinstance(scenes, list) and len(scenes) > 0:
                    print("✅ Fixed and parsed JSON")
                    return scenes
            except:
                pass
            
            print("⚠️  Using fallback scenes")
            return self._create_fallback_scenes()
    
    def _create_fallback_scenes(self) -> List[Dict[str, Any]]:
        """Generate fallback scenes when AI generation fails"""
        return [
            {"scene_number": 1, "speaker": "Narrator", "text": "Welcome to this audio experience.", "emotion": "neutral"},
            {"scene_number": 2, "speaker": "Host", "text": "Let's explore this fascinating topic together.", "emotion": "excited"},
            {"scene_number": 3, "speaker": "Narrator", "text": "Thank you for listening.", "emotion": "neutral"}
        ]
    
    def save_scenes(self, scenes: List[Dict[str, Any]], output_file: Path) -> None:
        """Save scenes to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Scenes saved to: {output_file}")
