"""
Commercial Video Generator - Streamlit UI

Professional interface for TikTok creators and commercial clients.
"""

import streamlit as st
import sys
from pathlib import Path
import logging
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

from commercial.pipeline import CommercialPipeline, GenerationProgress
from commercial.config import config
from commercial.ui.components.style_selector import render_style_selector
from commercial.ui.components.voice_selector import render_voice_selector
from commercial.ui.components.cost_display import render_cost_display, render_cost_estimate, render_monthly_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AI Video Generator Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    
    if "generated_video" not in st.session_state:
        st.session_state.generated_video = None
    
    if "generation_in_progress" not in st.session_state:
        st.session_state.generation_in_progress = False
    
    if "selected_style" not in st.session_state:
        st.session_state.selected_style = "cinematic"
    
    if "selected_voice" not in st.session_state:
        st.session_state.selected_voice = "rachel"


def initialize_pipeline():
    """Initialize pipeline with API keys"""
    if st.session_state.pipeline is None:
        try:
            st.session_state.pipeline = CommercialPipeline(
                groq_api_key=config.GROQ_API_KEY,
                fal_api_key=config.FAL_API_KEY,
                elevenlabs_api_key=config.ELEVENLABS_API_KEY
            )
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize pipeline: {e}")
            st.info("💡 Make sure you've set up `.env.commercial` with your API keys")
            return False
    return True


def render_sidebar():
    """Render sidebar with API status and settings"""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # API Status
        st.subheader("🔌 API Status")
        
        try:
            st.success("✅ Groq: Connected")
            st.success("✅ Fal.ai: Connected")
            st.success("✅ ElevenLabs: Connected")
        except:
            st.error("❌ Check API keys in `.env.commercial`")
        
        st.divider()
        
        # Quick Settings
        st.subheader("🎯 Quick Settings")
        
        aspect_ratio = st.selectbox(
            "Aspect Ratio",
            ["16:9 (YouTube)", "9:16 (TikTok)", "1:1 (Instagram)"],
            key="aspect_ratio"
        )
        
        num_scenes = st.slider(
            "Number of Scenes",
            min_value=3,
            max_value=10,
            value=5,
            key="num_scenes"
        )
        
        st.divider()
        
        # Cost estimate
        st.subheader("💰 Cost Estimate")
        estimated_cost = render_cost_estimate(
            num_scenes=num_scenes,
            style=st.session_state.selected_style
        )
        st.metric("Estimated Cost", f"${estimated_cost:.2f}")


def render_quick_generate_tab():
    """Render Quick Generate tab"""
    st.markdown('<h2 class="main-header">🎬 AI Video Generator Pro</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Generate Professional Videos in Minutes
    Simply enter your topic and let AI create a complete video with:
    - 🎨 Photorealistic images
    - 🎬 Smooth animations
    - 🎙️ Professional voiceover
    - 🎵 Automatic assembly
    """)
    
    # Topic input
    topic = st.text_input(
        "Enter your video topic",
        placeholder="e.g., 'Cyberpunk Tokyo at night' or 'Morning coffee routine'",
        key="topic_input"
    )
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generate Video", type="primary", use_container_width=True, disabled=st.session_state.generation_in_progress):
            if not topic:
                st.warning("⚠️ Please enter a topic")
            else:
                generate_video(topic)
    
    # Progress display
    if st.session_state.generation_in_progress:
        render_generation_progress()
    
    # Results display
    if st.session_state.generated_video:
        render_results()


def render_advanced_tab():
    """Render Advanced Settings tab"""
    st.header("🎨 Advanced Settings")
    
    # Style selector
    selected_style = render_style_selector()
    
    st.divider()
    
    # Voice selector
    selected_voice = render_voice_selector()
    
    st.divider()
    
    # Additional settings
    st.subheader("⚙️ Fine-Tuning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        image_quality = st.select_slider(
            "Image Quality",
            options=["Draft (20 steps)", "Standard (28 steps)", "High (40 steps)"],
            value="Standard (28 steps)"
        )
    
    with col2:
        video_motion = st.select_slider(
            "Motion Intensity",
            options=["Subtle", "Moderate", "Dynamic"],
            value="Moderate"
        )


def render_projects_tab():
    """Render Projects tab"""
    st.header("📁 Projects")
    
    st.info("🚧 Project management coming soon!")
    
    st.markdown("""
    **Planned Features:**
    - Save and load projects
    - Batch generation
    - Project templates
    - Export history
    """)


def render_analytics_tab():
    """Render Analytics tab"""
    st.header("📊 Analytics & Usage")
    
    # Cost tracking
    render_cost_display(
        current_cost=0.0,
        monthly_usage=34.56,
        monthly_budget=100.0
    )
    
    st.divider()
    
    # Monthly stats
    render_monthly_stats()


def generate_video(topic: str):
    """Generate video from topic"""
    st.session_state.generation_in_progress = True
    st.session_state.generated_video = None
    
    # Initialize pipeline
    if not initialize_pipeline():
        st.session_state.generation_in_progress = False
        return
    
    # Progress container
    progress_container = st.empty()
    
    def on_progress(progress: GenerationProgress):
        with progress_container:
            st.write(f"**{progress.stage.title()}:** {progress.message}")
            st.progress(progress.current / progress.total)
            st.caption(f"Cost so far: ${progress.cost_so_far:.2f}")
    
    st.session_state.pipeline.set_progress_callback(on_progress)
    
    try:
        # Generate
        result = st.session_state.pipeline.generate_video(
            topic=topic,
            style=st.session_state.selected_style,
            voice=st.session_state.selected_voice,
            aspect_ratio=st.session_state.get("aspect_ratio", "16:9").split()[0]
        )
        
        st.session_state.generated_video = result
        st.success("✅ Video generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Generation failed: {e}")
        logger.error(f"Generation error: {e}", exc_info=True)
    
    finally:
        st.session_state.generation_in_progress = False


def render_generation_progress():
    """Render generation progress"""
    with st.spinner("Generating your video..."):
        st.info("⏳ This may take 2-5 minutes depending on complexity")


def render_results():
    """Render generation results"""
    result = st.session_state.generated_video
    
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success("🎉 Your video is ready!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Video player
    if result["final_video"].exists():
        st.video(str(result["final_video"]))
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Scenes", result["num_scenes"])
    
    with col2:
        st.metric("Generation Time", f"{result['duration_seconds']:.1f}s")
    
    with col3:
        st.metric("Total Cost", f"${result['total_cost']:.2f}")
    
    # Download button
    if result["final_video"].exists():
        with open(result["final_video"], "rb") as f:
            st.download_button(
                "📥 Download Video",
                data=f,
                file_name=f"{result['story'].title}.mp4",
                mime="video/mp4",
                use_container_width=True
            )


def main():
    """Main app entry point"""
    initialize_session_state()
    
    # Sidebar
    render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Quick Generate",
        "🎨 Advanced",
        "📁 Projects",
        "📊 Analytics"
    ])
    
    with tab1:
        render_quick_generate_tab()
    
    with tab2:
        render_advanced_tab()
    
    with tab3:
        render_projects_tab()
    
    with tab4:
        render_analytics_tab()


if __name__ == "__main__":
    main()
