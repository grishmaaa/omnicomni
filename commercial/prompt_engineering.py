"""
Prompt Engineering Module

Provides style presets, templates, and custom prompt building for video generation.
"""

from typing import Dict, List
from datetime import datetime

# Style presets for different video types
STYLE_PRESETS = {
    'cinematic': {
        'name': 'Cinematic',
        'description': 'Hollywood-style dramatic visuals with epic cinematography',
        'icon': '🎬',
        'prompt_suffix': 'cinematic lighting, dramatic composition, film grain, anamorphic lens, epic scale',
        'voice_style': 'dramatic',
        'pacing': 'slow',
        'music_mood': 'epic'
    },
    'documentary': {
        'name': 'Documentary',
        'description': 'Educational and informative with clear narration',
        'icon': '📚',
        'prompt_suffix': 'documentary photography, natural lighting, authentic, educational, clear details',
        'voice_style': 'authoritative',
        'pacing': 'medium',
        'music_mood': 'neutral'
    },
    'social_media': {
        'name': 'Social Media',
        'description': 'Fast-paced, engaging content for Instagram/TikTok',
        'icon': '📱',
        'prompt_suffix': 'vibrant colors, high contrast, trendy, eye-catching, modern aesthetic',
        'voice_style': 'energetic',
        'pacing': 'fast',
        'music_mood': 'upbeat'
    },
    'educational': {
        'name': 'Educational',
        'description': 'Clear explanations with visual aids and diagrams',
        'icon': '🎓',
        'prompt_suffix': 'clean design, infographic style, clear diagrams, professional, educational',
        'voice_style': 'friendly',
        'pacing': 'medium',
        'music_mood': 'calm'
    },
    'corporate': {
        'name': 'Corporate',
        'description': 'Professional business presentation style',
        'icon': '💼',
        'prompt_suffix': 'professional, clean, corporate aesthetic, modern office, business setting',
        'voice_style': 'professional',
        'pacing': 'medium',
        'music_mood': 'corporate'
    },
    'artistic': {
        'name': 'Artistic',
        'description': 'Creative and experimental visual style',
        'icon': '🎨',
        'prompt_suffix': 'artistic, creative, abstract elements, unique perspective, experimental',
        'voice_style': 'contemplative',
        'pacing': 'varied',
        'music_mood': 'ambient'
    }
}

# Prompt templates for common use cases
PROMPT_TEMPLATES = {
    'explainer': {
        'name': 'Explainer Video',
        'template': 'Create an explainer video about {topic}. Break down the concept into simple, easy-to-understand segments. Focus on clarity and visual examples.',
        'placeholders': ['topic']
    },
    'tutorial': {
        'name': 'Tutorial',
        'template': 'Create a step-by-step tutorial on {topic}. Show each step clearly with visual demonstrations. Make it easy to follow along.',
        'placeholders': ['topic']
    },
    'product_demo': {
        'name': 'Product Demo',
        'template': 'Create a product demonstration for {product}. Highlight key features, benefits, and use cases. Show the product in action.',
        'placeholders': ['product']
    },
    'story': {
        'name': 'Story/Narrative',
        'template': 'Tell a compelling story about {topic}. Create a narrative arc with beginning, middle, and end. Use emotional storytelling.',
        'placeholders': ['topic']
    },
    'comparison': {
        'name': 'Comparison',
        'template': 'Compare and contrast {item1} vs {item2}. Show the differences and similarities. Help viewers make an informed decision.',
        'placeholders': ['item1', 'item2']
    },
    'news_summary': {
        'name': 'News Summary',
        'template': 'Summarize the latest news about {topic}. Present key facts and developments. Keep it concise and informative.',
        'placeholders': ['topic']
    }
}


def get_style_preset(style_key: str) -> Dict:
    """Get style preset configuration"""
    return STYLE_PRESETS.get(style_key, STYLE_PRESETS['cinematic'])


def get_all_styles() -> Dict:
    """Get all available style presets"""
    return STYLE_PRESETS


def get_template(template_key: str) -> Dict:
    """Get prompt template"""
    return PROMPT_TEMPLATES.get(template_key, PROMPT_TEMPLATES['explainer'])


def get_all_templates() -> Dict:
    """Get all available templates"""
    return PROMPT_TEMPLATES


def build_enhanced_prompt(base_topic: str, style: str = 'cinematic', 
                         custom_additions: str = '') -> str:
    """
    Build enhanced prompt with style preset
    
    Args:
        base_topic: Base topic/description
        style: Style preset key
        custom_additions: Additional custom prompt text
        
    Returns:
        str: Enhanced prompt with style modifiers
    """
    style_preset = get_style_preset(style)
    
    enhanced = base_topic
    
    # Add custom additions if provided
    if custom_additions:
        enhanced += f". {custom_additions}"
    
    # Add style suffix
    enhanced += f". Style: {style_preset['prompt_suffix']}"
    
    return enhanced


def apply_template(template_key: str, **kwargs) -> str:
    """
    Apply a prompt template with placeholders
    
    Args:
        template_key: Template identifier
        **kwargs: Values for template placeholders
        
    Returns:
        str: Filled template
    """
    template = get_template(template_key)
    
    try:
        return template['template'].format(**kwargs)
    except KeyError as e:
        missing = str(e).strip("'")
        raise ValueError(f"Missing required placeholder: {missing}")


def save_prompt_to_history(user_id: int, prompt: str, style: str, metadata: Dict = None):
    """
    Save prompt to user's history
    
    Args:
        user_id: User database ID
        prompt: The prompt text
        style: Style preset used
        metadata: Additional metadata (template, custom additions, etc.)
    """
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    import json
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Create prompt_history table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prompt_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                prompt TEXT NOT NULL,
                style VARCHAR(50),
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            INSERT INTO prompt_history (user_id, prompt, style, metadata)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, prompt, style, json.dumps(metadata) if metadata else None))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Failed to save prompt history: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_prompt_history(user_id: int, limit: int = 10) -> List[Dict]:
    """Get user's recent prompts"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, prompt, style, metadata, created_at
            FROM prompt_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        return [dict(row) for row in cur.fetchall()]
        
    finally:
        cur.close()
        conn.close()


# Quality presets for video generation
QUALITY_PRESETS = {
    'standard': {
        'name': 'Standard (720p)',
        'resolution': '1280x720',
        'bitrate': '2500k',
        'fps': 24
    },
    'hd': {
        'name': 'HD (1080p)',
        'resolution': '1920x1080',
        'bitrate': '5000k',
        'fps': 30
    },
    '4k': {
        'name': '4K (2160p)',
        'resolution': '3840x2160',
        'bitrate': '15000k',
        'fps': 30
    }
}


def get_quality_preset(quality_key: str) -> Dict:
    """Get quality preset configuration"""
    return QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS['standard'])
