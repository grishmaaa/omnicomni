"""
Style Selector Component

Provides visual style presets for image generation.
"""

import streamlit as st
from typing import Dict


STYLE_PRESETS = {
    "cinematic": {
        "name": "🎬 Cinematic",
        "description": "Hollywood-style dramatic lighting and composition",
        "keywords": "cinematic, dramatic lighting, film grain, 35mm lens",
        "example": "Perfect for storytelling and emotional scenes"
    },
    "photorealistic": {
        "name": "📸 Photorealistic",
        "description": "Ultra-realistic photography style",
        "keywords": "photorealistic, sharp focus, natural lighting, DSLR",
        "example": "Best for product demos and realistic scenarios"
    },
    "anime": {
        "name": "🎨 Anime",
        "description": "Japanese animation style",
        "keywords": "anime style, vibrant colors, cel shading",
        "example": "Great for creative and stylized content"
    },
    "tiktok_viral": {
        "name": "📱 TikTok Viral",
        "description": "Trendy, eye-catching social media style",
        "keywords": "vibrant, high contrast, trending aesthetic",
        "example": "Optimized for social media engagement"
    },
    "minimalist": {
        "name": "⚪ Minimalist",
        "description": "Clean, simple, modern aesthetic",
        "keywords": "minimalist, clean background, simple composition",
        "example": "Professional and clean look"
    }
}


def render_style_selector() -> str:
    """
    Render style selector component
    
    Returns:
        Selected style key
    """
    st.subheader("🎨 Visual Style")
    
    # Create columns for style cards
    cols = st.columns(3)
    
    selected_style = st.session_state.get("selected_style", "cinematic")
    
    for i, (key, style) in enumerate(STYLE_PRESETS.items()):
        col = cols[i % 3]
        
        with col:
            # Style card
            is_selected = (key == selected_style)
            
            if st.button(
                style["name"],
                key=f"style_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_style = key
                selected_style = key
            
            # Description
            st.caption(style["description"])
            
            # Example
            with st.expander("ℹ️ Details"):
                st.write(f"**Use case:** {style['example']}")
                st.code(style["keywords"], language=None)
    
    return selected_style


def get_style_keywords(style: str) -> str:
    """Get keywords for a style"""
    return STYLE_PRESETS.get(style, STYLE_PRESETS["cinematic"])["keywords"]
