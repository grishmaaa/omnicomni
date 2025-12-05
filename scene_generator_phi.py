"""
Open Scene Generator - Uses Fully Open Models
No access requests or approvals needed!
Uses Microsoft Phi-2 or GPT-2 - smaller but accessible
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict, Any
import re


class OpenSceneGenerator:
    # Fully open models that anyone can use
    OPEN_MODELS = [
        "microsoft/phi-2",  # 2.7B, excellent quality, fully open
        "gpt2-large",       # 774M, fallback option
        "gpt2-medium",      # 355M, smaller fallback
    ]
    
    def __init__(self):
        """Initialize with an open model"""
        print("\n" + "="*70)
        print("OPEN SOURCE SCENE GENERATOR")
        print("="*70)
        print("\nUsing fully open models - no access requests needed!\n")
        
        self.model = None
        self.tokenizer = None
        self.model_name = None
        
        for model_name in self.OPEN_MODELS:
            print(f"Trying: {model_name}")
            if self._try_load_model(model_name):
                self.model_name = model_name
                print(f"\n✓ Successfully loaded: {model_name}\n")
                break
        
        if self.model is None:
            raise RuntimeError("Could not load any model")
    
    def _try_load_model(self, model_name: str) -> bool:
        """Try to load a model"""
        try:
            print(f"  Loading... (this may take a moment on first run)")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            # Set pad token if not present  
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True
            )
            
            self.tokenizer = tokenizer
            self.model = model
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
            return False
    
    def get_director_prompt(self, topic: str) -> str:
        """Create prompt for scene generation"""
        prompt = f"""Create 4 audio drama scenes about: {topic}

Format as JSON array with these fields for each scene:
- scene_number (1-4)
- speaker (character name)
- text (1-2 sentences of dialogue)
- emotion (mysterious, excited, serious, or dramatic)

Example:
[{{"scene_number":1,"speaker":"Narrator","text":"The story begins.","emotion":"mysterious"}}]

JSON:"""
        return prompt
    
    def generate_scenes(self, topic: str, max_new_tokens: int = 800) -> List[Dict[str, Any]]:
        """Generate scenes"""
        print(f"\n{'='*60}")
        print(f"Generating scenes: {topic}")
        print(f"Model: {self.model_name}")
        print(f"{'='*60}\n")
        
        prompt = self.get_director_prompt(topic)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(self.model.device)
        
        # Generate
        print("Generating...")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract scenes
        scenes = self._extract_json_scenes(generated)
        
        print(f"\n✓ Generated {len(scenes)} scenes")
        return scenes
    
    def _extract_json_scenes(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON from text"""
        # Try to find JSON
        json_start = text.find('[')
        json_end = text.rfind(']') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = text[json_start:json_end]
            try:
                scenes = json.loads(json_str)
                if isinstance(scenes, list) and len(scenes) > 0:
                    # Validate and fix scenes
                    valid_scenes = []
                    for i, scene in enumerate(scenes):
                        if isinstance(scene, dict):
                            valid_scenes.append({
                                "scene_number": scene.get("scene_number", i+1),
                                "speaker": scene.get("speaker", "Narrator"),
                                "text": scene.get("text", "..."),
                                "emotion": scene.get("emotion", "neutral")
                            })
                    if valid_scenes:
                        return valid_scenes
            except:
                pass
        
        # Fallback: create scenes based on topic
        print("Using fallback scene generation...")
        return self._create_topic_scenes(text)
    
    def _create_topic_scenes(self, generated_text: str) -> List[Dict[str, Any]]:
        """Create scenes from generated text"""
        # Split generated text into sentences
        sentences = [s.strip() for s in generated_text.split('.') if len(s.strip()) > 20]
        
        if len(sentences) >= 3:
            return [
                {"scene_number": 1, "speaker": "Narrator", "text": sentences[0] + ".", "emotion": "mysterious"},
                {"scene_number": 2, "speaker": "Explorer", "text": sentences[1] + ".", "emotion": "excited"},
                {"scene_number": 3, "speaker": "Scientist", "text": sentences[2] + ".", "emotion": "serious"},
                {"scene_number": 4, "speaker": "Narrator", "text": sentences[3] + "." if len(sentences) > 3 else "The story continues.", "emotion": "dramatic"}
            ]
        
        # Ultimate fallback
        return [
            {"scene_number": 1, "speaker": "Narrator", "text": "Our journey begins with an intriguing discovery.", "emotion": "mysterious"},
            {"scene_number": 2, "speaker": "Expert", "text": "This changes everything we thought we knew!", "emotion": "excited"},
            {"scene_number": 3, "speaker": "Leader", "text": "We must proceed carefully and consider all implications.", "emotion": "serious"},
            {"scene_number": 4, "speaker": "Narrator", "text": "And so the adventure continues into the unknown.", "emotion": "dramatic"}
        ]


if __name__ == "__main__":
    try:
        generator = OpenSceneGenerator()
        
        topic = "A mysterious signal from deep space"
        scenes = generator.generate_scenes(topic)
        
        print("\n" + "="*60)
        print("GENERATED SCENES")
        print("="*60)
        for scene in scenes:
            print(f"\n[Scene {scene['scene_number']}] {scene['speaker']} ({scene['emotion']})")
            print(f"  \"{scene['text']}\"")
        
        # Save
        with open("scenes_open.json", 'w', encoding='utf-8') as f:
            json.dump(scenes, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to: scenes_open.json")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
