"""
Terms & Conditions and Privacy Policy

Legal documents and acceptance flow for AI Video Generator
"""

import streamlit as st
from datetime import datetime

def show_terms_page():
    """Display Terms & Conditions page"""
    
    st.markdown("""
    <style>
    .terms-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .terms-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }
    
    .terms-section h3 {
        color: #2d3748;
        margin-top: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="terms-header">
        <h1>📜 Terms & Conditions</h1>
        <p>Last Updated: December 16, 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Terms Content
    st.markdown("""
    <div class="terms-section">
        <h3>1. Acceptance of Terms</h3>
        <p>
            By accessing and using AI Video Generator ("the Service"), you accept and agree to be bound by 
            the terms and provision of this agreement. If you do not agree to these terms, please do not 
            use the Service.
        </p>
    </div>
    
    <div class="terms-section">
        <h3>2. Description of Service</h3>
        <p>
            AI Video Generator provides an AI-powered platform for creating videos from text descriptions. 
            The Service includes:
        </p>
        <ul>
            <li>AI-generated scripts based on user input</li>
            <li>Automated image and video generation</li>
            <li>AI voice narration</li>
            <li>Video storage and management</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>3. User Accounts</h3>
        <p>
            To use the Service, you must:
        </p>
        <ul>
            <li>Create an account with accurate information</li>
            <li>Maintain the security of your password</li>
            <li>Be at least 13 years of age</li>
            <li>Not share your account with others</li>
        </ul>
        <p>
            You are responsible for all activities that occur under your account.
        </p>
    </div>
    
    <div class="terms-section">
        <h3>4. Content Ownership and Usage Rights</h3>
        <p>
            <strong>Your Content:</strong> You retain all rights to the videos you create using our Service.
        </p>
        <p>
            <strong>Our Rights:</strong> By using the Service, you grant us a license to:
        </p>
        <ul>
            <li>Store and process your content to provide the Service</li>
            <li>Use anonymized data to improve our AI models</li>
            <li>Display your content in our gallery (if you choose to make it public)</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>5. Acceptable Use Policy</h3>
        <p>
            You agree NOT to use the Service to create content that:
        </p>
        <ul>
            <li>Violates any laws or regulations</li>
            <li>Infringes on intellectual property rights</li>
            <li>Contains hate speech, violence, or adult content</li>
            <li>Spreads misinformation or spam</li>
            <li>Impersonates others or misrepresents identity</li>
        </ul>
        <p>
            We reserve the right to remove content and terminate accounts that violate these terms.
        </p>
    </div>
    
    <div class="terms-section">
        <h3>6. Subscription and Payment</h3>
        <p>
            <strong>Free Tier:</strong> Limited video generations per month
        </p>
        <p>
            <strong>Paid Subscriptions:</strong>
        </p>
        <ul>
            <li>Billed monthly or annually</li>
            <li>Auto-renewal unless cancelled</li>
            <li>No refunds for partial months</li>
            <li>Prices subject to change with 30 days notice</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>7. Service Availability</h3>
        <p>
            We strive for 99.9% uptime but do not guarantee uninterrupted service. We may:
        </p>
        <ul>
            <li>Perform scheduled maintenance</li>
            <li>Experience unexpected downtime</li>
            <li>Modify or discontinue features</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>8. Limitation of Liability</h3>
        <p>
            The Service is provided "as is" without warranties. We are not liable for:
        </p>
        <ul>
            <li>Loss of data or content</li>
            <li>Indirect or consequential damages</li>
            <li>Third-party actions or content</li>
        </ul>
        <p>
            Our total liability is limited to the amount you paid in the last 12 months.
        </p>
    </div>
    
    <div class="terms-section">
        <h3>9. Privacy Policy</h3>
        <p>
            <strong>Data We Collect:</strong>
        </p>
        <ul>
            <li>Account information (email, name)</li>
            <li>Usage data (videos created, topics)</li>
            <li>Technical data (IP address, browser)</li>
        </ul>
        <p>
            <strong>How We Use Data:</strong>
        </p>
        <ul>
            <li>Provide and improve the Service</li>
            <li>Send important updates</li>
            <li>Analyze usage patterns</li>
        </ul>
        <p>
            <strong>Data Protection:</strong>
        </p>
        <ul>
            <li>Encrypted storage and transmission</li>
            <li>No selling of personal data</li>
            <li>GDPR and CCPA compliant</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>10. Termination</h3>
        <p>
            You may delete your account at any time. We may suspend or terminate your account if you:
        </p>
        <ul>
            <li>Violate these terms</li>
            <li>Engage in fraudulent activity</li>
            <li>Abuse the Service</li>
        </ul>
    </div>
    
    <div class="terms-section">
        <h3>11. Changes to Terms</h3>
        <p>
            We may update these terms at any time. Continued use of the Service after changes 
            constitutes acceptance of the new terms.
        </p>
    </div>
    
    <div class="terms-section">
        <h3>12. Contact Information</h3>
        <p>
            For questions about these terms, contact us at:
        </p>
        <p>
            <strong>Email:</strong> legal@aivideogen.com<br>
            <strong>Address:</strong> [Your Company Address]
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Acceptance checkbox (for signup flow)
    if st.session_state.get('show_acceptance', False):
        st.markdown("### ✅ Agreement")
        accepted = st.checkbox(
            "I have read and agree to the Terms & Conditions and Privacy Policy",
            key="terms_checkbox"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.page = "signup"
                st.session_state.show_acceptance = False
                st.rerun()
        
        with col2:
            if st.button("Continue to Signup →", use_container_width=True, type="primary", disabled=not accepted):
                st.session_state.terms_accepted = True
                st.session_state.page = "signup"
                st.session_state.show_acceptance = False
                st.rerun()
    else:
        if st.button("← Back to Home", use_container_width=False):
            st.session_state.page = "landing"
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Terms & Conditions - AI Video Generator",
        page_icon="📜",
        layout="wide"
    )
    show_terms_page()
