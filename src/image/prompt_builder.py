"""
Advanced Prompt Builder for Image Generation
Optimized for Flux-Schnell and Stable Diffusion

Implements structured prompt assembly with:
- Style presets (Cinematic, Anime, Photorealistic, etc.)
- Optimal keyword ordering for diffusion models
- Configurable quality tags
- Visual field separation (subject, action, environment, lighting, camera)

Follows OmniComni architecture patterns.
"""

from typing import Dict, Optional
from enum import Enum


# ============================================================================
# CONFIGURABLE CONSTANTS
# ============================================================================

class QualityLevel(str, Enum):
    """Quality preset levels"""
    ULTRA = "ultra"
    HIGH = "high"
    STANDARD = "standard"


# Quality tags for different levels
QUALITY_TAGS = {
    QualityLevel.ULTRA: "8k uhd, ultra detailed, masterpiece, professional photography, award winning",
    QualityLevel.HIGH: "4k, sharp focus, highly detailed, professional",
    QualityLevel.STANDARD: "hd, good quality, detailed"
}


# Style presets with their prefix keywords
STYLE_PRESETS = {
    "cinematic": {
        "prefix": "Cinematic film still, moody atmosphere, dramatic lighting, film grain",
        "suffix": "shot on Arri Alexa, shallow depth of field"
    },
    "anime": {
        "prefix": "Anime style, Studio Ghibli inspired, vibrant colors, cel-shaded",
        "suffix": "highly detailed anime art, trending on pixiv"
    },
    "photorealistic": {
        "prefix": "Photorealistic, natural lighting, realistic textures",
        "suffix": "professional photography, DSLR, 85mm lens"
    },
    "analog_film": {
        "prefix": "Analog film photography, Kodak Portra 400, film grain, warm tones",
        "suffix": "vintage aesthetic, nostalgic"
    },
    "concept_art": {
        "prefix": "Concept art, painterly style, atmospheric perspective",
        "suffix": "digital painting, artstation trending"
    },
    "cyberpunk": {
        "prefix": "Cyberpunk aesthetic, neon lights, high tech low life, dystopian",
        "suffix": "blade runner inspired, volumetric lighting"
    },
    "fantasy": {
        "prefix": "Fantasy art, magical atmosphere, ethereal lighting",
        "suffix": "epic composition, detailed environment"
    },
    "minimalist": {
        "prefix": "Minimalist style, clean composition, simple background",
        "suffix": "modern aesthetic, negative space"
    }
}


# ============================================================================
# PROMPT BUILDER
# ============================================================================

def build_flux_prompt(
    scene: Dict,
    global_style: str = "cinematic",
    quality: QualityLevel = QualityLevel.HIGH,
    include_negative: bool = False
) -> Dict[str, str]:
    """
    Build optimized prompt for Flux/Stable Diffusion from structured scene
    
    Prompt Assembly Order (optimized for Flux):
    1. Style Prefix
    2. Subject + Action (what's happening)
    3. Environment (where it's happening)
    4. Lighting + Camera (how it's captured)
    5. Quality Tags
    6. Style Suffix
    
    Args:
        scene: Scene dictionary with structured visual fields:
            - visual_subject: Main character/object details
            - visual_action: What they're doing
            - background_environment: Setting, location
            - lighting: Lighting conditions
            - camera_shot: Camera angle, framing
        global_style: Style preset name (default: "cinematic")
        quality: Quality level for technical tags
        include_negative: Whether to include negative prompt
        
    Returns:
        Dictionary with 'positive' and optionally 'negative' prompts
        
    Example:
        >>> scene = {
        ...     "visual_subject": "A cyberpunk detective",
        ...     "visual_action": "eating noodles",
        ...     "background_environment": "neon-lit Tokyo alley",
        ...     "lighting": "moody neon lighting",
        ...     "camera_shot": "medium close-up"
        ... }
        >>> prompts = build_flux_prompt(scene, "cinematic")
        >>> print(prompts['positive'])
    """
    
    # Get style preset (fallback to cinematic)
    style = STYLE_PRESETS.get(global_style.lower(), STYLE_PRESETS["cinematic"])
    
    # Extract visual fields (with fallbacks for compatibility)
    subject = scene.get("visual_subject", "")
    action = scene.get("visual_action", "")
    environment = scene.get("background_environment", "")
    lighting = scene.get("lighting", "")
    camera = scene.get("camera_shot", "")
    
    # Fallback: Use old 'image_prompt' field if new fields missing
    if not any([subject, action, environment, lighting, camera]):
        old_prompt = scene.get("image_prompt", "")
        if old_prompt:
            # Use legacy prompt as-is
            positive = f"{style['prefix']}, {old_prompt}, {QUALITY_TAGS[quality]}, {style['suffix']}"
            return {
                "positive": positive,
                "negative": get_negative_prompt() if include_negative else ""
            }
    
    # Build structured prompt components
    components = []
    
    # 1. Style Prefix
    components.append(style['prefix'])
    
    # 2. Subject + Action (core narrative)
    subject_action = f"{subject} {action}".strip()
    if subject_action:
        components.append(subject_action)
    
    # 3. Environment
    if environment:
        components.append(environment)
    
    # 4. Lighting + Camera
    lighting_camera = f"{lighting}, {camera}".strip(", ")
    if lighting_camera:
        components.append(lighting_camera)
    
    # 5. Quality Tags
    components.append(QUALITY_TAGS[quality])
    
    # 6. Style Suffix
    components.append(style['suffix'])
    
    # Assemble final prompt
    positive = ", ".join(filter(None, components))
    
    result = {"positive": positive}
    
    if include_negative:
        result["negative"] = get_negative_prompt()
    
    return result


def get_negative_prompt() -> str:
    """
    Standard negative prompt for Flux/SD
    
    Returns:
        String of negative keywords to avoid
    """
    return (
        "ugly, poorly drawn, bad anatomy, wrong anatomy, extra limb, "
        "missing limb, floating limbs, disconnected limbs, mutation, "
        "mutated, ugly, disgusting, blurry, amputation, watermark, "
        "text, signature, low quality, jpeg artifacts"
    )


def build_character_consistent_prompt(
    scene: Dict,
    character_description: str,
    global_style: str = "cinematic",
    quality: QualityLevel = QualityLevel.HIGH
) -> Dict[str, str]:
    """
    Build prompt with consistent character description across scenes
    
    Args:
        scene: Scene with visual fields
        character_description: Persistent character details (e.g., "tall man in blue coat")
        global_style: Style preset
        quality: Quality level
        
    Returns:
        Prompts dictionary
        
    Use Case: Maintain same character across multiple scenes
    """
    # Override visual_subject with consistent character description
    enhanced_scene = scene.copy()
    action = enhanced_scene.get("visual_action", "")
    enhanced_scene["visual_subject"] = f"{character_description} {action}".strip()
    enhanced_scene["visual_action"] = ""  # Absorbed into subject
    
    return build_flux_prompt(enhanced_scene, global_style, quality)


def list_available_styles() -> list:
    """
    Get list of available style presets
    
    Returns:
        List of style preset names
    """
    return list(STYLE_PRESETS.keys())


def get_style_description(style_name: str) -> Dict[str, str]:
    """
    Get detailed description of a style preset
    
    Args:
        style_name: Name of style preset
        
    Returns:
        Dictionary with prefix and suffix keywords
    """
    return STYLE_PRESETS.get(style_name.lower(), {})


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """Example: Cyberpunk detective eating noodles"""
    
    # Example structured scene
    scene = {
        "id": 0,
        "visual_subject": "A weary cyberpunk detective in a rain-soaked trench coat, neon-lit face with augmented eyes",
        "visual_action": "slurping ramen noodles from a steaming bowl with chopsticks",
        "background_environment": "dimly lit noodle stand in a narrow Tokyo alley, holographic signs flickering overhead",
        "lighting": "moody neon lighting, cyan and magenta reflections on wet pavement, volumetric fog",
        "camera_shot": "medium close-up, slightly low angle, shallow depth of field focusing on detective"
    }
    
    # Build prompts
    prompts = build_flux_prompt(scene, global_style="cyberpunk", quality=QualityLevel.HIGH)
    
    print("=" * 70)
    print("EXAMPLE: Cyberpunk Detective Eating Noodles")
    print("=" * 70)
    print("\n📋 Input Scene Fields:")
    print(f"  Subject: {scene['visual_subject'][:60]}...")
    print(f"  Action: {scene['visual_action']}")
    print(f"  Environment: {scene['background_environment'][:60]}...")
    print(f"  Lighting: {scene['lighting'][:60]}...")
    print(f"  Camera: {scene['camera_shot']}")
    
    print("\n🎨 Generated Prompt:")
    print(prompts['positive'])
    print("\n" + "=" * 70)
    
    # Show available styles
    print("\n📚 Available Style Presets:")
    for style in list_available_styles():
        print(f"  - {style}")
