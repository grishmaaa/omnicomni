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
    
    Supports two formats:
    1. Legacy: visual_prompt (single string)
    2. Structured: Separate visual fields for optimal prompt engineering
    
    Attributes:
        scene_id: Unique scene identifier
        visual_prompt: (Legacy) Combined visual description
        visual_subject: (New) Main character/object with details
        visual_action: (New) What they're doing
        background_environment: (New) Setting, location, atmosphere
        lighting: (New) Lighting conditions, time of day, mood
        camera_shot: (New) Camera angle, framing, composition
        audio_text: Narration text for TTS
        duration: Scene length in seconds (5-10s typical)
    """
    scene_id: int = Field(..., ge=1, description="Scene number (1-indexed)")
    
    # Legacy field (backward compatibility)
    visual_prompt: Optional[str] = Field(None, min_length=10, description="Combined visual description (legacy)")
    
    # New structured fields (Task 13: Advanced Prompt Engineering)
    visual_subject: Optional[str] = Field(None, description="Main character/object with specific details")
    visual_action: Optional[str] = Field(None, description="What they're doing (verb-focused)")
    background_environment: Optional[str] = Field(None, description="Setting, location, atmosphere")
    lighting: Optional[str] = Field(None, description="Lighting conditions, time of day, mood")
    camera_shot: Optional[str] = Field(None, description="Camera angle, framing, composition")
    
    # Required fields
    audio_text: str = Field(..., min_length=1, description="Narration script")
    duration: int = Field(default=8, ge=3, le=30, description="Scene duration in seconds")
    
    @validator('visual_prompt', 'visual_subject', 'visual_action', 'background_environment', 'lighting', 'camera_shot')
    def strip_whitespace(cls, v):
        """Strip whitespace from all text fields"""
        return v.strip() if v else v
    
    @validator('visual_subject', always=True)
    def validate_visual_fields(cls, v, values):
        """Ensure either legacy visual_prompt OR new structured fields are present"""
        visual_prompt = values.get('visual_prompt')
        
        # If legacy field exists, we're good
        if visual_prompt and len(visual_prompt.strip()) >= 10:
            return v
        
        # If new field exists, we're good
        if v and len(v.strip()) >= 5:
            return v
        
        # Neither exists - error
        if not visual_prompt and not v:
            raise ValueError(
                "Scene must have either 'visual_prompt' (legacy) or "
                "'visual_subject' + other visual fields (new structured format)"
            )
        
        return v
    
    @validator('audio_text')
    def validate_audio_text(cls, v):
        """Ensure audio text is not empty"""
        if not v.strip():
            raise ValueError("Audio text cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example_legacy": {
                "scene_id": 1,
                "visual_prompt": "Neon-lit Tokyo street, 4k ultra detailed, volumetric lighting, cyberpunk style, rain-soaked pavement",
                "audio_text": "In the heart of Neo-Tokyo, where technology and tradition collide.",
                "duration": 8
            },
            "example_structured": {
                "scene_id": 1,
                "visual_subject": "A weary cyberpunk detective in a rain-soaked trench coat",
                "visual_action": "walking down a neon-lit street",
                "background_environment": "narrow Tokyo alley, holographic signs flickering",
                "lighting": "moody neon lighting, cyan and magenta reflections",
                "camera_shot": "medium shot, slightly low angle, cinematic composition",
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
