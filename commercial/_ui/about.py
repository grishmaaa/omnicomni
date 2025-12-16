"""
About Page for AI Video Generator

Information about the platform, how it works, and contact details.
"""

import streamlit as st

def show_about_page():
    """Display the about page"""
    
    # Custom CSS
    st.markdown("""
    <style>
    .about-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
    }
    
    .content-box {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border-left: 5px solid #667eea;
    }
    
    .team-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="about-header">
        <h1>About AI Video Generator</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Empowering creators with AI-powered video generation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mission
    st.markdown('<h2 class="section-title">🎯 Our Mission</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="content-box">
        <p style="font-size: 1.1rem; line-height: 1.8; color: #4a5568;">
            We believe that everyone should have the power to create professional-quality videos, 
            regardless of their technical expertise or budget. Our AI-powered platform democratizes 
            video creation, making it accessible, affordable, and incredibly easy.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # How It Works (Detailed)
    st.markdown('<h2 class="section-title">⚙️ How It Works</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-box">
            <h3>🤖 AI Script Generation</h3>
            <p>Our advanced language models analyze your topic and create engaging, 
            well-structured scripts tailored to your needs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>🎨 Image Generation</h3>
            <p>State-of-the-art image AI creates stunning visuals that perfectly 
            match your script's narrative.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-box">
            <h3>🎥 Video Creation</h3>
            <p>Images are transformed into smooth, cinematic video clips with 
            professional transitions.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="content-box">
            <h3>🎙️ Voice Narration</h3>
            <p>Natural-sounding AI voices bring your script to life with perfect 
            timing and emotion.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown('<h2 class="section-title">🔧 Technology Stack</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🧠 AI Models**
        - OpenAI GPT-4
        - FLUX Image Generation
        - ElevenLabs Voice AI
        """)
    
    with col2:
        st.markdown("""
        **🔐 Security**
        - Firebase Authentication
        - PostgreSQL Database
        - End-to-end Encryption
        """)
    
    with col3:
        st.markdown("""
        **⚡ Infrastructure**
        - Cloud-based Processing
        - CDN Delivery
        - Auto-scaling
        """)
    
    # Use Cases
    st.markdown('<h2 class="section-title">💼 Use Cases</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📚 Education**
        - Explainer videos
        - Course content
        - Tutorials
        
        **📱 Social Media**
        - Instagram Reels
        - TikTok content
        - YouTube shorts
        """)
    
    with col2:
        st.markdown("""
        **💼 Business**
        - Product demos
        - Marketing videos
        - Presentations
        
        **🎬 Content Creation**
        - Documentaries
        - Storytelling
        - News summaries
        """)
    
    # Contact
    st.markdown('<h2 class="section-title">📧 Contact Us</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-box">
        <p><strong>Email:</strong> support@aivideogen.com</p>
        <p><strong>Twitter:</strong> @AIVideoGen</p>
        <p><strong>Discord:</strong> Join our community</p>
        <p style="margin-top: 1.5rem;">
            Have questions or feedback? We'd love to hear from you!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home", use_container_width=False):
        st.session_state.page = "landing"
        st.rerun()


if __name__ == "__main__":
    st.set_page_config(
        page_title="About - AI Video Generator",
        page_icon="🎬",
        layout="wide"
    )
    show_about_page()
