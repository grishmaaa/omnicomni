"""
Pydantic Models for Scene Validation

Business reason: Validates LLM output to fail fast and save API costs.
Ensures scenes have required fields before expensive TTS processing.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class SceneModel(BaseModel):
    """
    Individual scene in a video storyboard
    
    Attributes:
        scene_id: Unique scene identifier
        visual_prompt: Stable Diffusion/Flux optimized description
        audio_text: Narration text for TTS
        duration: Scene length in seconds (5-10s typical)
    """
    scene_id: int = Field(..., ge=1, description="Scene number (1-indexed)")
    visual_prompt: str = Field(..., min_length=10, description="Detailed visual description for AI image generation")
    audio_text: str = Field(..., min_length=1, description="Narration script")
    duration: int = Field(default=8, ge=3, le=30, description="Scene duration in seconds")
    
    @validator('visual_prompt')
    def validate_visual_prompt(cls, v):
        """Ensure visual prompt has quality markers"""
        if len(v.strip()) < 10:
            raise ValueError("Visual prompt too short - must be detailed")
        return v.strip()
    
    @validator('audio_text')
    def validate_audio_text(cls, v):
        """Ensure audio text is not empty"""
        if not v.strip():
            raise ValueError("Audio text cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "scene_id": 1,
                "visual_prompt": "Neon-lit Tokyo street, 4k ultra detailed, volumetric lighting, cyberpunk style, rain-soaked pavement",
                "audio_text": "In the heart of Neo-Tokyo, where technology and tradition collide.",
                "duration": 8
            }
        }


class StoryboardModel(BaseModel):
    """
    Complete storyboard with metadata
    
    Attributes:
        topic: Original user topic
        scenes: List of validated scenes
        total_duration: Total video length in seconds
    """
    topic: str = Field(..., min_length=1)
    scenes: List[SceneModel] = Field(..., min_items=1, max_items=10)
    
    @property
    def total_duration(self) -> int:
        """Calculate total duration from all scenes"""
        return sum(scene.duration for scene in self.scenes)
    
    @property
    def scene_count(self) -> int:
        """Number of scenes in storyboard"""
        return len(self.scenes)
    
    @validator('scenes')
    def validate_scene_ids(cls, scenes):
        """Ensure scene IDs are sequential and unique"""
        ids = [s.scene_id for s in scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate scene IDs found")
        return scenes
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "The history of coffee",
                "scenes": [
                    {
                        "scene_id": 1,
                        "visual_prompt": "Ancient Ethiopian highlands, 4k, golden hour lighting",
                        "audio_text": "Coffee's story begins in Ethiopia.",
                        "duration": 8
                    }
                ]
            }
        }


def validate_llm_output(raw_scenes: List[dict], topic: str) -> StoryboardModel:
    """
    Validate LLM-generated scenes using Pydantic
    
    Fails fast if data is malformed to save API costs.
    
    Args:
        raw_scenes: Raw list of scene dicts from LLM
        topic: Original topic for metadata
        
    Returns:
        Validated StoryboardModel
        
    Raises:
        ValidationError: If scenes don't match schema
        
    Example:
        >>> raw = [{"scene_id": 1, "visual_prompt": "...", "audio_text": "...", "duration": 8}]
        >>> storyboard = validate_llm_output(raw, "Coffee history")
        >>> print(storyboard.total_duration)
        8
    """
    return StoryboardModel(topic=topic, scenes=raw_scenes)
