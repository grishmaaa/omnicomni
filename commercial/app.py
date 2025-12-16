"""
AI Video Generator - Production App with Authentication

Features:
- Firebase authentication (login/signup)
- PostgreSQL database for user data and video metadata
- User-specific video gallery
- Session management with temp asset cleanup
"""

# Load environment variables FIRST, before any other imports
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env.commercial from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env.commercial"
load_dotenv(env_path)
print(f"DEBUG: Loaded .env from {env_path}")
print(f"DEBUG: .env file exists: {env_path.exists()}")
print(f"DEBUG: DATABASE_URL loaded: {bool(os.getenv('DATABASE_URL'))}")

import streamlit as st
import sys
import importlib.util

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from auth import (
    is_authenticated, login_user, signup_user, 
    logout_user, get_current_user, init_firebase
)
from database import (
    init_db, get_user_by_uid, create_user,
    save_video_metadata, get_user_videos, update_last_login
)
from utils.session_manager import (
    clear_temp_assets, archive_video,
    generate_thumbnail, get_video_duration
)


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# Initialize Services
# ============================================================================

def initialize_services():
    """Initialize Firebase and Database (runs once)"""
    try:
        init_firebase()
        init_db()
        return True
    except Exception as e:
        st.error(f"❌ Service initialization failed: {e}")
        return False


# ============================================================================
# Authentication UI
# ============================================================================

def show_login_page():
    """Display login/signup page"""
    st.title("🎬 AI Video Generator")
    st.markdown("---")
    
    # Tabs for login and signup
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary"):
            if email and password:
                with st.spinner("Logging in..."):
                    user = login_user(email, password)
                    
                    if user:
                        # Update last login in database
                        update_last_login(user['uid'])
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
            else:
                st.warning("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")
        display_name = st.text_input("Display Name (optional)", key="signup_name")
        
        if st.button("Sign Up", type="primary"):
            if new_email and new_password:
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        try:
                            # Create Firebase user
                            user = signup_user(new_email, new_password, display_name)
                            
                            # Create database record
                            create_user(
                                user['uid'],
                                user['email'],
                                user['display_name']
                            )
                            
                            # Auto-login
                            st.session_state.user = user
                            st.success("✅ Account created successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Signup failed: {e}")
            else:
                st.warning("Please enter email and password")


# ============================================================================
# Main Application
# ============================================================================

def show_main_app():
    """Display main application for authenticated users"""
    
    # Get current user
    user = get_current_user()
    firebase_uid = user['uid']
    
    # Get user from database
    user_db = get_user_by_uid(firebase_uid)
    if not user_db:
        # Create if doesn't exist
        user_db = create_user(firebase_uid, user['email'], user['display_name'])
    
    # ========================================================================
    # Sidebar - User Info & Video Gallery
    # ========================================================================
    
    with st.sidebar:
        st.title("🎬 AI Video Generator")
        st.markdown("---")
        
        # User info
        st.markdown(f"👤 **{user['display_name']}**")
        st.caption(user['email'])
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
        
        st.markdown("---")
        st.subheader("📚 Your Videos")
        
        # Load user's videos from database
        videos = get_user_videos(user_db['id'])
        
        if videos:
            for video in videos:
                with st.container():
                    # Show thumbnail if exists
                    if video['thumbnail_path'] and Path(video['thumbnail_path']).exists():
                        st.image(video['thumbnail_path'], use_container_width=True)
                    
                    st.markdown(f"**{video['topic']}**")
                    st.caption(video['created_at'].strftime("%Y-%m-%d %H:%M"))
                    
                    # Download button
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
    
    # ========================================================================
    # Main Area - Video Generation
    # ========================================================================
    
    st.title("🎬 AI Video Generator")
    
    # Topic input
    topic = st.text_input(
        "Enter your video topic:",
        placeholder="e.g., The Future of Renewable Energy"
    )
    
    # Generate button
    if st.button("🎬 Generate Video", type="primary", disabled=not topic):
        if topic:
            try:
                # Clear temp assets
                with st.spinner("Clearing previous session..."):
                    clear_temp_assets()
                
                # Load modules
                def load_mod(name, path):
                    spec = importlib.util.spec_from_file_location(name, path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    return mod
                
                src = Path(__file__).parent / "src"
                
                # Step 1: Generate script
                with st.spinner("📝 Step 1/5: Generating script..."):
                    load_mod("s1", src / "1_script_gen.py").generate_script(
                        topic, num_scenes=5, style="cinematic"
                    )
                    st.success("✅ Script generated!")
                
                # Step 2: Generate images
                with st.spinner("🎨 Step 2/5: Generating images..."):
                    load_mod("s2", src / "2_image_gen.py").generate_images()
                    st.success("✅ Images generated!")
                
                # Step 3: Generate videos
                with st.spinner("🎥 Step 3/5: Generating videos (5-8 min)..."):
                    load_mod("s3", src / "3_video_gen.py").generate_videos()
                    st.success("✅ Videos generated!")
                
                # Step 4: Generate audio
                with st.spinner("🎵 Step 4/5: Generating audio..."):
                    load_mod("s4", src / "4_audio_gen.py").generate_audio()
                    st.success("✅ Audio generated!")
                
                # Step 5: Assemble final video
                with st.spinner("🎬 Step 5/5: Assembling final video..."):
                    load_mod("s5", Path(__file__).parent / "complete_assembler.py").main()
                    st.success("✅ Video assembled!")
                
                # Archive video
                video_path = Path(__file__).parent / "assets" / "FINAL_VIDEO.mp4"
                
                if video_path.exists():
                    with st.spinner("💾 Saving to your library..."):
                        # Archive to user folder
                        archived_path, thumbnail_path = archive_video(
                            firebase_uid, topic, video_path
                        )
                        
                        # Get video duration
                        duration = get_video_duration(archived_path)
                        
                        # Save to database
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
                    
                    # Show video
                    st.video(str(archived_path))
                    
                    # Download button
                    with open(archived_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Download Video",
                            f,
                            file_name=f"{topic}.mp4",
                            mime="video/mp4"
                        )
                    
                    st.rerun()  # Refresh to show in gallery
                
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # Show existing videos
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
                            file_name=f"{video['topic']}.mp4",
                            mime="video/mp4",
                            key=f"main_download_{video['id']}"
                        )
    else:
        st.info("Your video library is empty. Generate your first video above!")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize services
    if not initialize_services():
        st.stop()
    
    # Check authentication
    if not is_authenticated():
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
