"""
AI Video Generator - Production App

Multi-page application with landing, authentication, and video generation.
"""

# Load environment variables FIRST
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env.commercial"
load_dotenv(env_path)

import streamlit as st
import sys
import importlib.util

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import pages
from _ui.landing import show_landing_page
from _ui.about import show_about_page
from _ui.terms import show_terms_page
from _ui.pricing import show_pricing_page

# Import custom modules
from database import (
    init_db, get_user_by_uid, create_user,
    save_video_metadata, get_user_videos, update_last_login
)
from utils.session_manager import (
    clear_temp_assets, archive_video,
    generate_thumbnail, get_video_duration
)
from subscription import (
    create_subscription, get_user_subscription,
    can_generate_video, increment_usage,
    get_user_usage, get_tier_info
)
from auth_supabase import (
    is_authenticated, login_user, signup_user,
    verify_password, logout_user, get_current_user
)

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="auto"
)

# ============================================================================
# Initialize Services
# ============================================================================

def initialize_services():
    """Initialize Database"""
    try:
        init_db()
        return True
    except Exception as e:
        st.error(f"❌ Service initialization failed: {e}")
        return False

# ============================================================================
# Authentication Pages
# ============================================================================

def show_login_page():
    """Login page"""
    st.title("🔐 Login")
    st.markdown("---")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", type="primary", use_container_width=True):
            if email and password:
                with st.spinner("Logging in..."):
                    try:
                        # verify_password returns user data dict or None
                        user_data = verify_password(email, password)
                        
                        if user_data:
                            # Store user in session
                            st.session_state.user = user_data
                            
                            # Update last login in database
                            try:
                                update_last_login(user_data['uid'])
                            except:
                                pass  # Don't fail login if update fails
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    except Exception as e:
                        st.error(f"❌ Login failed: {e}")
            else:
                st.warning("Please enter email and password")
    
    with col2:
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    
    st.markdown("---")
    st.markdown("Don't have an account? [Sign up](#)")
    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()


def show_signup_page():
    """Signup page with terms acceptance"""
    st.title("📝 Create Account")
    st.markdown("---")
    
    # Check if terms accepted
    if not st.session_state.get('terms_accepted', False):
        st.info("📜 Please read and accept our Terms & Conditions to continue")
        
        if st.button("View Terms & Conditions", type="primary"):
            st.session_state.show_acceptance = True
            st.session_state.page = "terms"
            st.rerun()
        
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.rerun()
        return
    
    # Signup form
    email = st.text_input("Email")
    password = st.text_input("Password (min 6 characters)", type="password")
    display_name = st.text_input("Display Name (optional)")
    
    # Terms checkbox
    terms_check = st.checkbox("I agree to the Terms & Conditions", value=True, disabled=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Sign Up", type="primary", use_container_width=True):
            if email and password:
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            user = signup_user(email, password, display_name)
                            user_db = create_user(user['uid'], user['email'], user['display_name'])
                            # Create free subscription for new user
                            create_subscription(user_db['id'], 'free')
                            st.session_state.user = user
                            st.session_state.terms_accepted = False  # Reset for next signup
                            st.success("✅ Account created successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Signup failed: {e}")
            else:
                st.warning("Please enter email and password")
    
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.terms_accepted = False
            st.session_state.page = "landing"
            st.rerun()


# ============================================================================
# Main Application (Authenticated)
# ============================================================================

def show_main_app():
    """Main video generation app"""
    user = get_current_user()
    firebase_uid = user['uid']
    
    user_db = get_user_by_uid(firebase_uid)
    if not user_db:
        user_db = create_user(firebase_uid, user['email'], user['display_name'])
    
    # Get or create subscription
    subscription = get_user_subscription(user_db['id'])
    if not subscription:
        subscription = create_subscription(user_db['id'], 'free')
    
    tier = subscription['tier']
    tier_info = get_tier_info(tier)
    usage = get_user_usage(user_db['id'])
    
    # Sidebar
    with st.sidebar:
        st.title("🎬 AI Video Generator")
        
        if is_authenticated():
            user = get_current_user()
            st.write(f"👤 {user['display_name']}")
            st.write(f"📧 {user['email']}")
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
                logout_user()
                st.session_state.user = None
                st.success("Logged out successfully!")
                st.rerun()
            
            st.markdown("---")
            
            # Navigation
            page = st.radio(
                "Navigation",
                ["Dashboard", "Generate Video", "My Videos", "Subscription", "Pricing"],
                label_visibility="collapsed"
            )
        
        # Subscription info
        st.markdown("---")
        st.markdown(f"**Plan:** {tier_info['name']}")
        
        limit = tier_info['videos_per_month']
        current_usage = usage['videos_generated']
        
        if limit == -1:
            st.caption("✨ Unlimited videos")
        else:
            st.caption(f"📊 {current_usage}/{limit} videos this month")
            progress = min(current_usage / limit, 1.0) if limit > 0 else 0
            st.progress(progress)
        
        if tier == 'free':
            if st.button("⬆️ Upgrade Plan", use_container_width=True):
                st.session_state.page = "pricing"
                st.rerun()
        
        st.markdown("---")
        st.subheader("📚 Your Videos")
        
        videos = get_user_videos(user_db['id'])
        
        if videos:
            for video in videos:
                with st.container():
                    if video['thumbnail_path'] and Path(video['thumbnail_path']).exists():
                        st.image(video['thumbnail_path'], use_container_width=True)
                    
                    st.markdown(f"**{video['topic']}**")
                    st.caption(video['created_at'].strftime("%Y-%m-%d %H:%M"))
                    
                    if Path(video['file_path']).exists():
                        with open(video['file_path'], 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f,
                                file_name=f"{video['topic']}.mp4",
                                mime="video/mp4",
                                key=f"download_{video['id']}",
                                use_container_width=True
                            )
                    
                    st.markdown("---")
        else:
            st.info("No videos yet. Generate your first one!")
    
    # Main Area - Video Generation
    st.title("🎬 AI Video Generator")
    
    # Import prompt engineering
    from prompt_engineering import (
        get_all_styles, build_enhanced_prompt,
        save_prompt_to_history, QUALITY_PRESETS
    )
    
    # Basic input
    topic = st.text_input(
        "Enter your video topic:",
        placeholder="e.g., The Future of Renewable Energy",
        help="Describe what you want your video to be about"
    )
    
    # Advanced options (expandable)
    with st.expander("⚙️ Advanced Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Style preset
            st.markdown("**🎨 Visual Style**")
            styles = get_all_styles()
            style_options = {k: f"{v['icon']} {v['name']}" for k, v in styles.items()}
            selected_style = st.selectbox(
                "Choose a style",
                options=list(style_options.keys()),
                format_func=lambda x: style_options[x],
                help="Visual style and mood for your video"
            )
            
            # Show style description
            st.caption(styles[selected_style]['description'])
            
            # Number of scenes
            num_scenes = st.slider(
                "Number of Scenes",
                min_value=3,
                max_value=10,
                value=5,
                help="More scenes = longer video"
            )
        
        with col2:
            # Quality preset
            st.markdown("**📺 Video Quality**")
            quality_options = {k: v['name'] for k, v in QUALITY_PRESETS.items()}
            
            # Check tier for quality access
            if tier == 'free':
                available_quality = ['standard']
                st.caption("⬆️ Upgrade to Pro for HD and 4K")
            elif tier == 'pro':
                available_quality = ['standard', 'hd']
                st.caption("⬆️ Upgrade to Enterprise for 4K")
            else:
                available_quality = list(quality_options.keys())
            
            selected_quality = st.selectbox(
                "Choose quality",
                options=available_quality,
                format_func=lambda x: quality_options[x]
            )
            
            # Custom prompt additions
            st.markdown("**✏️ Custom Additions**")
            custom_prompt = st.text_area(
                "Add custom instructions",
                placeholder="e.g., Focus on environmental impact, include statistics",
                height=100,
                help="Additional details to customize your video"
            )
    
    # Build enhanced prompt
    if topic:
        enhanced_prompt = build_enhanced_prompt(topic, selected_style, custom_prompt)
        
        # Show preview of enhanced prompt
        with st.expander("👁️ Preview Enhanced Prompt"):
            st.info(enhanced_prompt)
    
    # Generate button
    if st.button("🎬 Generate Video", type="primary", disabled=not topic):
        if topic:
            # Check usage limits
            can_generate, message = can_generate_video(user_db['id'], tier)
            
            if not can_generate:
                st.error(f"❌ {message}")
                if st.button("⬆️ Upgrade to Pro"):
                    st.session_state.page = "pricing"
                    st.rerun()
                return
            
            st.info(f"ℹ️ {message}")
            
            try:
                with st.spinner("Clearing previous session..."):
                    clear_temp_assets()
                
                def load_mod(name, path):
                    spec = importlib.util.spec_from_file_location(name, path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    return mod
                
                src = Path(__file__).parent / "src"
                
                with st.spinner("📝 Step 1/5: Generating script..."):
                    # Use enhanced prompt and selected parameters
                    load_mod("s1", src / "1_script_gen.py").generate_script(
                        enhanced_prompt, num_scenes=num_scenes, style=selected_style
                    )
                    st.success("✅ Script generated!")
                    
                    # Save prompt to history
                    save_prompt_to_history(
                        user_db['id'],
                        enhanced_prompt,
                        selected_style,
                        {'num_scenes': num_scenes, 'quality': selected_quality, 'custom': custom_prompt}
                    )
                
                with st.spinner("🎨 Step 2/5: Generating images..."):
                    load_mod("s2", src / "2_image_gen.py").generate_images()
                    st.success("✅ Images generated!")
                
                with st.spinner("🎥 Step 3/5: Generating videos (5-8 min)..."):
                    load_mod("s3", src / "3_video_gen.py").generate_videos()
                    st.success("✅ Videos generated!")
                
                with st.spinner("🎵 Step 4/5: Generating audio..."):
                    load_mod("s4", src / "4_audio_gen.py").generate_audio()
                    st.success("✅ Audio generated!")
                
                with st.spinner("🎬 Step 5/5: Assembling final video..."):
                    load_mod("s5", Path(__file__).parent / "complete_assembler.py").main()
                    st.success("✅ Video assembled!")
                
                video_path = Path(__file__).parent / "assets" / "FINAL_VIDEO.mp4"
                
                if video_path.exists():
                    with st.spinner("💾 Saving to your library..."):
                        archived_path, thumbnail_path = archive_video(
                            firebase_uid, topic, video_path
                        )
                        
                        duration = get_video_duration(archived_path)
                        
                        # Increment usage count
                        increment_usage(user_db['id'])
                        
                        save_video_metadata(
                            user_id=user_db['id'],
                            topic=topic,
                            file_path=str(archived_path),
                            thumbnail_path=str(thumbnail_path) if thumbnail_path else "",
                            duration_seconds=duration,
                            metadata={"num_scenes": 5, "style": "cinematic"}
                        )
                    
                    st.success("🎉 Video generation complete!")
                    st.balloons()
                    
                    # Display video
                    st.video(str(archived_path))
                    
                    # Advanced download options
                    st.markdown("### 📥 Download Options")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Main video download
                        with open(archived_path, 'rb') as f:
                            st.download_button(
                                "⬇️ Download Video (MP4)",
                                f,
                                file_name=f"{topic}.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )
                    
                    with col2:
                        # Audio-only download (if Pro+)
                        if tier in ['pro', 'enterprise']:
                            audio_path = Path(__file__).parent / "assets" / "final_audio.mp3"
                            if audio_path.exists():
                                with open(audio_path, 'rb') as f:
                                    st.download_button(
                                        "🎵 Download Audio Only",
                                        f,
                                        file_name=f"{topic}_audio.mp3",
                                        mime="audio/mpeg",
                                        use_container_width=True
                                    )
                        else:
                            st.button("🎵 Audio (Pro+)", disabled=True, use_container_width=True)
                    
                    with col3:
                        # Scene images download (if Pro+)
                        if tier in ['pro', 'enterprise']:
                            st.button("🖼️ Download Scenes", use_container_width=True, help="Coming soon")
                        else:
                            st.button("🖼️ Scenes (Pro+)", disabled=True, use_container_width=True)
                    
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("📚 Your Video Library")
    
    videos = get_user_videos(user_db['id'])
    
    if videos:
        cols = st.columns(3)
        for idx, video in enumerate(videos):
            with cols[idx % 3]:
                if video['thumbnail_path'] and Path(video['thumbnail_path']).exists():
                    st.image(video['thumbnail_path'])
                
                st.markdown(f"**{video['topic']}**")
                st.caption(f"{video['created_at'].strftime('%Y-%m-%d')} • {video['duration_seconds']}s")
                
                if Path(video['file_path']).exists():
                    with open(video['file_path'], 'rb') as f:
                        st.download_button(
                            "Download",
                            f,
                            file_name=f"{video['topic']}mp4",
                            mime="video/mp4",
                            key=f"main_download_{video['id']}"
                        )
    else:
        st.info("Your video library is empty. Generate your first video above!")


# ============================================================================
# Main Router
# ============================================================================

def main():
    """Main application router"""
    
    # Initialize services
    if not initialize_services():
        st.stop()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "landing"
    
    # Route to appropriate page
    if is_authenticated():
        show_main_app()
    else:
        page = st.session_state.get('page', 'landing')
        
        if page == "landing":
            show_landing_page()
        elif page == "about":
            show_about_page()
        elif page == "terms":
            show_terms_page()
        elif page == "login":
            show_login_page()
        elif page == "signup":
            show_signup_page()
        elif page == "pricing":
            show_pricing_page()
        else:
            show_landing_page()


if __name__ == "__main__":
    main()
