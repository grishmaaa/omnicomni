"""
Groq API Client for Story Generation

Uses Llama-3.3-70B for structured scene generation with JSON output.
"""

import json
import logging
from typing import List, Dict, Optional
from groq import Groq
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SceneData(BaseModel):
    """Structured scene data"""
    scene_id: int
    visual_subject: str = Field(..., description="Main character/object")
    visual_action: str = Field(..., description="What's happening")
    background_environment: str = Field(..., description="Setting/location")
    lighting: str = Field(..., description="Lighting conditions")
    camera_shot: str = Field(..., description="Camera angle/framing")
    narration: str = Field(..., description="Voiceover text")
    duration: float = Field(default=5.0, description="Scene duration in seconds")


class StoryResponse(BaseModel):
    """Complete story with multiple scenes"""
    title: str
    style: str
    scenes: List[SceneData]


class GroqClient:
    """
    Groq API client for structured story generation
    
    Features:
    - Llama-3.3-70B for fast, high-quality generation
    - Structured JSON output with Pydantic validation
    - Token usage tracking for cost monitoring
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
            model: Model ID (default: llama-3.3-70b-versatile)
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.total_tokens = 0
        
        logger.info(f"Initialized Groq client with model: {model}")
    
    def generate_story(
        self,
        topic: str,
        num_scenes: int = 5,
        style: str = "cinematic"
    ) -> StoryResponse:
        """
        Generate structured story from topic
        
        Args:
            topic: Video topic/theme
            num_scenes: Number of scenes to generate
            style: Visual style (cinematic, anime, photorealistic)
            
        Returns:
            StoryResponse with structured scenes
            
        Raises:
            ValueError: If generation fails or JSON is invalid
        """
        logger.info(f"Generating story for topic: '{topic}' ({num_scenes} scenes, {style} style)")
        
        # System prompt for structured output
        system_prompt = f"""You are a professional video scriptwriter specializing in {style} short-form content.

Generate a {num_scenes}-scene story for the topic: "{topic}"

CRITICAL: Respond ONLY with valid JSON matching this exact schema:
{{
  "title": "Engaging title",
  "style": "{style}",
  "scenes": [
    {{
      "scene_id": 1,
      "visual_subject": "Main character/object with specific details",
      "visual_action": "What they're doing (verb-focused)",
      "background_environment": "Setting, location, atmosphere",
      "lighting": "Lighting conditions, time of day, mood",
      "camera_shot": "Camera angle, framing (e.g., 'medium shot, 35mm lens')",
      "narration": "Voiceover text (15-25 words, engaging hook for first scene)",
      "duration": 5.0
    }}
  ]
}}

RULES:
1. Each scene must be visually distinct
2. Narration should be conversational and engaging
3. First scene MUST have a strong hook (first 3 seconds matter)
4. Visual descriptions should be simple (avoid "highly detailed", "intricate")
5. Use neutral/soft lighting for consistency
6. Camera shots: medium shot, wide shot, close-up (avoid extreme angles)
7. NO markdown, NO explanations, ONLY the JSON object"""

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate {num_scenes} scenes for: {topic}"}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Track token usage
            usage = response.usage
            self.total_tokens += usage.total_tokens
            
            logger.info(
                f"Groq response: {usage.total_tokens} tokens "
                f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})"
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            story_dict = json.loads(content)
            
            # Validate with Pydantic
            story = StoryResponse(**story_dict)
            
            logger.info(f"✅ Generated story: '{story.title}' with {len(story.scenes)} scenes")
            return story
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON from Groq: {e}")
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise ValueError(f"Story generation failed: {e}")
    
    def get_cost_estimate(self) -> float:
        """
        Estimate cost based on token usage
        
        Groq pricing (as of 2024):
        - Llama-3.3-70B: $0.59/1M input tokens, $0.79/1M output tokens
        - Average: ~$0.69/1M tokens
        
        Returns:
            Estimated cost in USD
        """
        cost_per_million = 0.69
        return (self.total_tokens / 1_000_000) * cost_per_million
    
    def reset_usage(self):
        """Reset token counter"""
        self.total_tokens = 0
        logger.debug("Reset token usage counter")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv(".env.commercial")
    
    client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))
    
    story = client.generate_story(
        topic="Cyberpunk Tokyo at night",
        num_scenes=5,
        style="cinematic"
    )
    
    print(f"\n📖 Story: {story.title}")
    print(f"Style: {story.style}")
    print(f"\nScenes:")
    for scene in story.scenes:
        print(f"\n  Scene {scene.scene_id}:")
        print(f"    Subject: {scene.visual_subject}")
        print(f"    Action: {scene.visual_action}")
        print(f"    Narration: {scene.narration}")
    
    print(f"\n💰 Cost: ${client.get_cost_estimate():.4f}")
