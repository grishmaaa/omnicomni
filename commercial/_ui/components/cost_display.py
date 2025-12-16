"""
Cost Display Component

Real-time cost tracking and budget monitoring.
"""

import streamlit as st
from typing import Dict, Optional
import plotly.graph_objects as go


def render_cost_display(
    current_cost: float = 0.0,
    estimated_cost: Optional[float] = None,
    monthly_usage: float = 0.0,
    monthly_budget: float = 100.0
) -> None:
    """
    Render cost display component
    
    Args:
        current_cost: Current generation cost
        estimated_cost: Estimated cost for pending generation
        monthly_usage: Total monthly usage
        monthly_budget: Monthly budget limit
    """
    st.subheader("💰 Cost Tracking")
    
    # Current generation cost
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Video",
            f"${current_cost:.2f}",
            delta=f"${estimated_cost:.2f} est." if estimated_cost else None
        )
    
    with col2:
        st.metric(
            "Monthly Usage",
            f"${monthly_usage:.2f}",
            delta=f"{(monthly_usage/monthly_budget)*100:.0f}% of budget"
        )
    
    with col3:
        remaining = monthly_budget - monthly_usage
        st.metric(
            "Remaining Budget",
            f"${remaining:.2f}",
            delta=f"{(remaining/monthly_budget)*100:.0f}%"
        )
    
    # Budget progress bar
    progress = min(monthly_usage / monthly_budget, 1.0)
    
    if progress < 0.7:
        color = "normal"
    elif progress < 0.9:
        color = "off"
    else:
        color = "inverse"
    
    st.progress(progress, text=f"Budget Usage: {progress*100:.1f}%")
    
    if progress >= 0.9:
        st.warning("⚠️ Approaching monthly budget limit!")
    
    # Cost breakdown
    with st.expander("📊 Cost Breakdown"):
        render_cost_breakdown()


def render_cost_breakdown():
    """Render detailed cost breakdown"""
    
    # Example cost breakdown
    breakdown = {
        "Story Generation (Groq)": 0.002,
        "Image Generation (FLUX)": 0.15,
        "Video Generation (Minimax)": 0.50,
        "Voice Synthesis (ElevenLabs)": 0.15
    }
    
    total = sum(breakdown.values())
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(breakdown.keys()),
        values=list(breakdown.values()),
        hole=0.3,
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'])
    )])
    
    fig.update_layout(
        title="Cost Distribution per Video",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.markdown("**Detailed Breakdown:**")
    for service, cost in breakdown.items():
        percentage = (cost / total) * 100
        st.write(f"- {service}: ${cost:.3f} ({percentage:.1f}%)")
    
    st.write(f"**Total:** ${total:.2f}")


def render_cost_estimate(
    num_scenes: int = 5,
    style: str = "cinematic",
    aspect_ratio: str = "16:9"
) -> float:
    """
    Estimate cost for generation
    
    Args:
        num_scenes: Number of scenes
        style: Visual style
        aspect_ratio: Video aspect ratio
        
    Returns:
        Estimated cost in USD
    """
    # Base costs per scene
    cost_per_scene = {
        "story": 0.002 / 5,  # $0.002 for 5 scenes
        "image": 0.03,       # FLUX.1-dev
        "video": 0.10,       # Minimax
        "voice": 0.03        # ElevenLabs (~100 chars)
    }
    
    total = sum(cost_per_scene.values()) * num_scenes
    
    # Style multiplier
    if style == "photorealistic":
        total *= 1.1  # More inference steps
    
    return total


def render_monthly_stats():
    """Render monthly usage statistics"""
    st.subheader("📈 Monthly Statistics")
    
    # Example data (would come from database in production)
    stats = {
        "videos_generated": 42,
        "total_cost": 34.56,
        "avg_cost_per_video": 0.82,
        "most_used_style": "Cinematic",
        "most_used_voice": "Rachel"
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Videos Generated", stats["videos_generated"])
        st.metric("Average Cost/Video", f"${stats['avg_cost_per_video']:.2f}")
    
    with col2:
        st.metric("Total Spent", f"${stats['total_cost']:.2f}")
        st.metric("Most Used Style", stats["most_used_style"])
    
    # Usage over time chart
    with st.expander("📊 Usage Over Time"):
        st.info("Chart would show daily/weekly usage trends")
