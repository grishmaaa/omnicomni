"""
Google Gemini API Client for Story Generation

Uses Gemini 1.5 Flash for fast, free structured scene generation with JSON output.
Perfect for India - no payment issues, generous free tier.
"""

import json
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
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


class GeminiClient:
    """
    Google Gemini API client for structured story generation
    
    Features:
    - Gemini 1.5 Flash for fast, free generation
    - Structured JSON output with Pydantic validation
    - Token usage tracking for cost monitoring
    - Free tier: 1M tokens/day, 15 RPM
    - Pay-as-you-go: $0.075/1M tokens (very cheap)
    """
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google AI Studio API key
            model: Model name (default: gemini-1.5-flash)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"
            }
        )
        self.total_tokens = 0
        
        logger.info(f"Initialized Gemini client with model: {model}")
    
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
        
        # Prompt for structured output
        prompt = f"""You are a professional video scriptwriter specializing in {style} short-form content.

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
7. NO markdown, NO explanations, ONLY the JSON object

Generate {num_scenes} scenes for: {topic}"""

        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Track token usage (approximate)
            # Gemini doesn't expose token counts directly, so we estimate
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimate
            response_tokens = len(response.text.split()) * 1.3
            self.total_tokens += int(prompt_tokens + response_tokens)
            
            logger.info(
                f"Gemini response: ~{int(prompt_tokens + response_tokens)} tokens "
                f"(estimated)"
            )
            
            # Parse JSON response
            content = response.text
            story_dict = json.loads(content)
            
            # Validate with Pydantic
            story = StoryResponse(**story_dict)
            
            logger.info(f"✅ Generated story: '{story.title}' with {len(story.scenes)} scenes")
            return story
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response.text[:500]}")
            raise ValueError(f"Invalid JSON from Gemini: {e}")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise ValueError(f"Story generation failed: {e}")
    
    def get_cost_estimate(self) -> float:
        """
        Estimate cost based on token usage
        
        Gemini 1.5 Flash pricing:
        - Free tier: 1M tokens/day
        - Pay-as-you-go: $0.075/1M input, $0.30/1M output
        - Average: ~$0.15/1M tokens
        
        Returns:
            Estimated cost in USD (returns 0 if within free tier)
        """
        FREE_TIER_DAILY = 1_000_000
        
        if self.total_tokens < FREE_TIER_DAILY:
            return 0.0  # Within free tier
        
        # Only charge for tokens beyond free tier
        billable_tokens = self.total_tokens - FREE_TIER_DAILY
        cost_per_million = 0.15  # Average of input/output
        return (billable_tokens / 1_000_000) * cost_per_million
    
    def reset_usage(self):
        """Reset token counter"""
        self.total_tokens = 0
        logger.debug("Reset token usage counter")


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv(".env.commercial")
    
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    
    story = client.generate_story(
        topic="The Art of Japanese Tea Ceremony",
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
    
    print(f"\n💰 Cost: ${client.get_cost_estimate():.4f} (FREE if within daily limit)")
