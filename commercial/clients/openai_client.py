"""
OpenAI API Client for Story Generation

Uses GPT-4o-mini for fast, reliable structured scene generation.
Most reliable option - works immediately with no setup issues.
"""

import json
import logging
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SceneData(BaseModel):
    """Structured scene data"""
    scene_id: int
    visual_subject: str
    visual_action: str
    background_environment: str
    lighting: str
    camera_shot: str
    narration: str
    duration: float = 5.0


class StoryResponse(BaseModel):
    """Complete story with multiple scenes"""
    title: str
    style: str
    scenes: List[SceneData]


class OpenAIClient:
    """OpenAI API client for story generation - most reliable option"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.total_tokens = 0
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    def generate_story(self, topic: str, num_scenes: int = 5, style: str = "cinematic") -> StoryResponse:
        # Prompt for cinematic advertisement-style narration
        prompt = f"""You are a world-class advertising copywriter creating a cinematic commercial.

Generate a {num_scenes}-scene story for: "{topic}"

CRITICAL NARRATION STYLE:
- Write like a PREMIUM ADVERTISEMENT (Apple, Nike, luxury brands)
- Emotional, inspiring, and captivating
- Short, powerful sentences with impact
- Use sensory language and emotion
- Create desire and wonder
- NO explanations or descriptions - pure storytelling
- Think: "This is your moment" not "The person is doing this"

EXAMPLE GOOD NARRATION:
"Every sip tells a story."
"Crafted with passion. Perfected through time."
"This is more than coffee. This is art."

EXAMPLE BAD NARRATION (avoid):
"In this scene, we see a barista making coffee in a café."
"The espresso machine is being used to brew coffee."

Respond ONLY with valid JSON:
{{
  "title": "Captivating title",
  "style": "{style}",
  "scenes": [
    {{
      "scene_id": 1,
      "visual_subject": "Main subject with specific details",
      "visual_action": "What's happening (verb-focused)",
      "background_environment": "Setting, location, atmosphere",
      "lighting": "Lighting mood",
      "camera_shot": "Camera angle (e.g., 'medium shot, 35mm')",
      "narration": "CINEMATIC ADVERTISEMENT STYLE - 8-15 words, emotional, inspiring",
      "duration": 5.0
    }}
  ]
}}

RULES:
1. Narration must sound like a LUXURY ADVERTISEMENT
2. Use emotion, not explanation
3. Create desire and aspiration
4. Short, punchy, memorable lines
5. First scene MUST hook immediately
6. Think: "How would Apple advertise this?"

Generate {num_scenes} scenes for: {topic}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            self.total_tokens += response.usage.total_tokens
            content = response.choices[0].message.content
            story_dict = json.loads(content)
            story = StoryResponse(**story_dict)
            
            logger.info(f"✅ Generated: '{story.title}' ({len(story.scenes)} scenes)")
            return story
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise ValueError(f"Story generation failed: {e}")
    
    def get_cost_estimate(self) -> float:
        """Estimate cost - GPT-4o-mini: $0.15/$0.60 per 1M tokens"""
        return (self.total_tokens / 1_000_000) * 0.30  # Average
    
    def reset_usage(self):
        self.total_tokens = 0
