"""
Scene Generator using Llama-3.2-3B
Generates JSON scenes from a topic using a director prompt
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from typing import List, Dict, Any
import re


class SceneGenerator:
    def __init__(self, model_name: str = "meta-llama/Llama-3.2-3B"):
        """Initialize the scene generator with Llama model"""
        print(f"Loading model: {model_name}")
        
        # Configure 4-bit quantization for memory efficiency
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
        """
        Create the director prompt for generating JSON scenes
        
        The prompt instructs the model to act as a creative director
        and generate a structured JSON array of scenes for the given topic.
        """
        prompt = f"""You are a creative director for audio storytelling. Your task is to create engaging scenes for an audio drama about the following topic:

Topic: {topic}

Generate a JSON array of 3-5 scenes. Each scene should have:
- "scene_number": The scene number (integer)
- "speaker": The character or narrator speaking (string)
- "text": The dialogue or narration (string, 1-3 sentences)
- "emotion": The emotional tone (string: neutral, excited, serious, mysterious, dramatic)

Requirements:
- Create a compelling narrative arc
- Keep each scene's text concise but engaging
- Vary the speakers and emotions
- Make it suitable for audio presentation

Output ONLY valid JSON, no additional text. Format:

[
  {{
    "scene_number": 1,
    "speaker": "Narrator",
    "text": "Your engaging opening line here.",
    "emotion": "mysterious"
  }},
  ...
]

JSON Output:"""
        
        return prompt
    
    def generate_scenes(self, topic: str, max_new_tokens: int = 1024, temperature: float = 0.7) -> List[Dict[str, Any]]:
        """
        Generate scenes from a topic
        
        Args:
            topic: The topic to generate scenes about
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more creative)
            
        Returns:
            List of scene dictionaries
        """
        print(f"\n{'='*60}")
        print(f"Generating scenes for topic: {topic}")
        print(f"{'='*60}\n")
        
        # Get the director prompt
        prompt = self.get_director_prompt(topic)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        print("Generating with Llama-3.2-3B...")
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
        
        # Extract JSON from the generated text
        scenes = self._extract_json_scenes(generated_text)
        
        print(f"\n✓ Generated {len(scenes)} scenes")
        return scenes
    
    def _extract_json_scenes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse JSON scenes from generated text
        
        Handles various formats and attempts to clean up the output
        """
        # Try to find JSON array in the text
        # Look for content after "JSON Output:" or similar markers
        json_start = text.find('[')
        json_end = text.rfind(']') + 1
        
        if json_start == -1 or json_end == 0:
            print("Warning: No JSON array found in output")
            print("Generated text:", text[-500:])  # Show last 500 chars
            return self._create_fallback_scenes()
        
        json_str = text[json_start:json_end]
        
        try:
            scenes = json.loads(json_str)
            
            # Validate structure
            if not isinstance(scenes, list):
                raise ValueError("JSON is not a list")
            
            # Ensure all required fields are present
            required_fields = {"scene_number", "speaker", "text", "emotion"}
            for scene in scenes:
                if not all(field in scene for field in required_fields):
                    raise ValueError(f"Scene missing required fields: {scene}")
            
            return scenes
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Attempting to fix JSON...")
            
            # Try to fix common JSON issues
            json_str = json_str.replace("'", '"')  # Replace single quotes
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)
            
            try:
                scenes = json.loads(json_str)
                return scenes
            except:
                print("Could not parse JSON, using fallback scenes")
                return self._create_fallback_scenes()
    
    def _create_fallback_scenes(self) -> List[Dict[str, Any]]:
        """Create fallback scenes if generation fails"""
        return [
            {
                "scene_number": 1,
                "speaker": "Narrator",
                "text": "Welcome to this audio experience. Let's explore an interesting topic together.",
                "emotion": "neutral"
            },
            {
                "scene_number": 2,
                "speaker": "Host",
                "text": "Today we'll dive deep into the subject and uncover fascinating insights.",
                "emotion": "excited"
            },
            {
                "scene_number": 3,
                "speaker": "Narrator",
                "text": "Thank you for listening. Stay tuned for more engaging content.",
                "emotion": "neutral"
            }
        ]
    
    def save_scenes(self, scenes: List[Dict[str, Any]], output_file: str):
        """Save scenes to a JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Scenes saved to: {output_file}")


if __name__ == "__main__":
    # Test the scene generator
    generator = SceneGenerator()
    
    # Example topic
    topic = "The discovery of a mysterious ancient artifact in the Amazon rainforest"
    
    # Generate scenes
    scenes = generator.generate_scenes(topic)
    
    # Print scenes
    print("\n" + "="*60)
    print("GENERATED SCENES")
    print("="*60)
    for scene in scenes:
        print(f"\nScene {scene['scene_number']} - {scene['speaker']} ({scene['emotion']})")
        print(f"  {scene['text']}")
    
    # Save to file
    generator.save_scenes(scenes, "scenes.json")
