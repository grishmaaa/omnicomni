"""
Voice Selector Component

Provides voice selection for ElevenLabs synthesis.
"""

import streamlit as st
from typing import Dict


VOICE_LIBRARY = {
    "rachel": {
        "name": "Rachel",
        "gender": "Female",
        "accent": "American",
        "description": "Calm, professional, perfect for narration",
        "use_case": "Corporate videos, tutorials, documentaries"
    },
    "adam": {
        "name": "Adam",
        "gender": "Male",
        "accent": "American",
        "description": "Deep, authoritative voice",
        "use_case": "Movie trailers, serious content"
    },
    "bella": {
        "name": "Bella",
        "gender": "Female",
        "accent": "American",
        "description": "Soft, friendly, approachable",
        "use_case": "Social media, lifestyle content"
    },
    "antoni": {
        "name": "Antoni",
        "gender": "Male",
        "accent": "American",
        "description": "Well-rounded, versatile",
        "use_case": "General purpose, storytelling"
    },
    "elli": {
        "name": "Elli",
        "gender": "Female",
        "accent": "American",
        "description": "Emotional, expressive",
        "use_case": "Drama, emotional content"
    },
    "josh": {
        "name": "Josh",
        "gender": "Male",
        "accent": "American",
        "description": "Young, energetic",
        "use_case": "TikTok, youth-oriented content"
    }
}


def render_voice_selector() -> str:
    """
    Render voice selector component
    
    Returns:
        Selected voice key
    """
    st.subheader("🎙️ Voice Selection")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        gender_filter = st.selectbox(
            "Gender",
            ["All", "Male", "Female"],
            key="voice_gender_filter"
        )
    
    with col2:
        use_case_filter = st.selectbox(
            "Use Case",
            ["All", "TikTok", "Corporate", "Storytelling"],
            key="voice_usecase_filter"
        )
    
    # Filter voices
    filtered_voices = {
        key: voice for key, voice in VOICE_LIBRARY.items()
        if (gender_filter == "All" or voice["gender"] == gender_filter)
    }
    
    # Voice selection
    selected_voice = st.session_state.get("selected_voice", "rachel")
    
    for key, voice in filtered_voices.items():
        is_selected = (key == selected_voice)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{voice['name']}** ({voice['gender']}, {voice['accent']})")
            st.caption(voice['description'])
            st.caption(f"💡 {voice['use_case']}")
        
        with col2:
            if st.button(
                "Select" if not is_selected else "✓ Selected",
                key=f"voice_{key}",
                type="primary" if is_selected else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_voice = key
                selected_voice = key
        
        st.divider()
    
    return selected_voice


def get_voice_settings(voice: str) -> Dict:
    """Get recommended settings for a voice"""
    # Default settings
    settings = {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    }
    
    # Voice-specific adjustments
    if voice == "elli":
        settings["style"] = 0.3  # More expressive
    elif voice == "adam":
        settings["stability"] = 0.7  # More consistent
    
    return settings
