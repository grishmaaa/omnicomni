"""
Landing Page for AI Video Generator

Modern, responsive landing page with hero section, features, and CTA.
"""

import streamlit as st
from pathlib import Path

def show_landing_page():
    """Display the landing page"""
    
    # Custom CSS for landing page
    st.markdown("""
    <style>
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        opacity: 0.95;
    }
    
    .cta-button {
        display: inline-block;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        background: white;
        color: #667eea;
        border-radius: 50px;
        text-decoration: none;
        margin: 0.5rem;
        transition: transform 0.2s;
    }
    
    .cta-button:hover {
        transform: scale(1.05);
    }
    
    /* Features Section */
    .feature-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
        border: 2px solid #e9ecef;
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #2d3748;
    }
    
    .feature-description {
        color: #718096;
        line-height: 1.6;
    }
    
    /* Stats Section */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 3rem 0;
        flex-wrap: wrap;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #718096;
        margin-top: 0.5rem;
    }
    
    /* How It Works */
    .step-container {
        display: flex;
        align-items: center;
        margin: 2rem 0;
        padding: 1.5rem;
        background: white;
        border-radius: 15px;
        border-left: 5px solid #667eea;
    }
    
    .step-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin-right: 1.5rem;
        min-width: 60px;
    }
    
    .step-content h3 {
        margin: 0 0 0.5rem 0;
        color: #2d3748;
    }
    
    .step-content p {
        margin: 0;
        color: #718096;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🎬 AI Video Generator</h1>
        <p class="hero-subtitle">Transform Your Ideas into Stunning Videos in Minutes</p>
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">
            Powered by cutting-edge AI technology. No video editing skills required.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Get Started Free", use_container_width=True, type="primary"):
                st.session_state.page = "signup"
                st.rerun()
        with col_b:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
    
    st.markdown("---")
    
    # Stats Section
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">10K+</div>
            <div class="stat-label">Videos Created</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">5K+</div>
            <div class="stat-label">Happy Users</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">99%</div>
            <div class="stat-label">Satisfaction Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features Section
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>✨ Powerful Features</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered</div>
            <div class="feature-description">
                Advanced AI generates scripts, images, and narration automatically
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Lightning Fast</div>
            <div class="feature-description">
                Create professional videos in minutes, not hours
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">Customizable</div>
            <div class="feature-description">
                Choose styles, themes, and customize every aspect
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">Video Library</div>
            <div class="feature-description">
                Access all your videos anytime, anywhere
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Secure & Private</div>
            <div class="feature-description">
                Your data is encrypted and never shared
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <div class="feature-title">Easy Download</div>
            <div class="feature-description">
                Download videos in high quality instantly
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # How It Works
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>🚀 How It Works</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="step-container">
        <div class="step-number">1</div>
        <div class="step-content">
            <h3>Enter Your Topic</h3>
            <p>Simply describe what you want your video to be about</p>
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-number">2</div>
        <div class="step-content">
            <h3>AI Does the Magic</h3>
            <p>Our AI generates script, images, videos, and narration</p>
        </div>
    </div>
    
    <div class="step-container">
        <div class="step-number">3</div>
        <div class="step-content">
            <h3>Download & Share</h3>
            <p>Get your professional video ready to share anywhere</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Final CTA
    st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem 0;'>Ready to Create Amazing Videos?</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎬 Start Creating Now", use_container_width=True, type="primary", key="bottom_cta"):
            st.session_state.page = "signup"
            st.rerun()
    
    # Footer
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("Pricing", use_container_width=True):
            st.session_state.page = "pricing"
            st.rerun()
    
    with col2:
        if st.button("About", use_container_width=True):
            st.session_state.page = "about"
            st.rerun()
    
    with col3:
        if st.button("Terms", use_container_width=True):
            st.session_state.page = "terms"
            st.rerun()
    
    with col4:
        if st.button("Privacy", use_container_width=True):
            st.session_state.page = "terms"
            st.rerun()
    
    with col5:
        if st.button("Contact", use_container_width=True):
            st.session_state.page = "about"
            st.rerun()
    
    st.markdown("""
    <div style='text-align: center; color: #718096; padding: 2rem 0;'>
        <p>© 2025 AI Video Generator. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Video Generator",
        page_icon="🎬",
        layout="wide"
    )
    show_landing_page()
