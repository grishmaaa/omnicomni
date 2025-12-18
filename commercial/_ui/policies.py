"""
Legal and Policy Pages for Razorpay Compliance
"""

import streamlit as st


def show_terms_page():
    """Terms and Conditions page"""
    st.title("📜 Terms and Conditions")
    st.markdown("---")
    
    st.markdown("""
    **Last Updated:** January 2025
    
    ## 1. ACCEPTANCE OF TERMS
    
    By accessing and using OmniComni AI Video Generator ("Service"), you accept and agree to be bound by these Terms of Service.
    
    ## 2. SERVICE DESCRIPTION
    
    OmniComni provides AI-powered video generation services through a web-based platform. Users can create videos from text prompts using advanced AI technology.
    
    ## 3. SUBSCRIPTION PLANS
    
    ### Available Plans:
    - **Starter:** $9.99/month - 10 videos, HD quality
    - **Professional:** $29.99/month - 50 videos, Full HD quality  
    - **Enterprise:** $700/month - Unlimited videos, 4K quality, API access
    
    ### Billing:
    - All plans billed monthly in advance
    - Auto-renewal unless cancelled
    - Prices subject to change with 30 days notice
    
    ## 4. USER OBLIGATIONS
    
    You agree to:
    - Provide accurate registration information
    - Maintain account security
    - Not share account credentials
    - Use service for lawful purposes only
    - Not generate illegal, harmful, or offensive content
    - Comply with all applicable laws
    
    ## 5. PROHIBITED USES
    
    You may NOT use the service to:
    - Generate content that violates copyright
    - Create deepfakes or misleading content
    - Harass, threaten, or harm others
    - Violate any laws or regulations
    - Reverse engineer the platform
    
    ## 6. INTELLECTUAL PROPERTY
    
    ### Your Content:
    - You retain ownership of prompts and inputs
    - You grant us license to process your content
    
    ### Generated Videos:
    - **Starter/Pro:** Personal use license
    - **Enterprise:** Commercial use license
    
    ## 7. PAYMENT & REFUNDS
    
    - Payments processed through Razorpay
    - All major payment methods accepted
    - Refunds: Pro-rated within 7 days of billing
    - No refunds for partial usage
    
    ## 8. LIMITATION OF LIABILITY
    
    - Service provided "as is"
    - No warranty of fitness for particular purpose
    - Not liable for indirect or consequential damages
    - Maximum liability limited to fees paid in last 12 months
    
    ## 9. CONTACT
    
    **Email:** legal@omnicomni.ai  
    **Support:** support@omnicomni.ai  
    **Website:** https://omnicomni.ai
    """)


def show_privacy_page():
    """Privacy Policy page"""
    st.title("🔒 Privacy Policy")
    st.markdown("---")
    
    st.markdown("""
    **Last Updated:** January 2025
    
    ## 1. INFORMATION WE COLLECT
    
    ### Personal Information:
    - Email address
    - Name
    - Payment information (processed by Razorpay)
    
    ### Usage Data:
    - Video generation history
    - Prompts and inputs
    - IP address
    - Browser type
    - Usage statistics
    
    ## 2. HOW WE USE YOUR INFORMATION
    
    We use your information to:
    - Provide and improve our service
    - Process payments
    - Send service updates
    - Provide customer support
    - Analyze usage patterns
    - Prevent fraud and abuse
    
    ## 3. DATA SECURITY
    
    - All data encrypted in transit (TLS 1.3)
    - Data encrypted at rest (AES-256)
    - Regular security audits
    - Secure data centers
    - Access controls and monitoring
    
    ## 4. DATA SHARING
    
    We DO NOT sell your data. We share data only with:
    - Payment processors (Razorpay)
    - Cloud service providers (for hosting)
    - Analytics services (anonymized data)
    
    ## 5. YOUR RIGHTS
    
    You have the right to:
    - Access your data
    - Delete your account
    - Export your data
    - Opt-out of marketing emails
    - Request data correction
    
    ## 6. COOKIES
    
    We use cookies for:
    - Session management
    - Analytics
    - Preferences
    
    You can disable cookies in your browser settings.
    
    ## 7. DATA RETENTION
    
    - Active accounts: Data retained indefinitely
    - Deleted accounts: Data deleted within 30 days
    - Backups: Retained for 90 days
    
    ## 8. GDPR COMPLIANCE
    
    For EU users:
    - Right to access
    - Right to erasure
    - Right to portability
    - Right to object
    
    ## 9. CONTACT
    
    For privacy concerns:
    
    **Email:** privacy@omnicomni.ai  
    **Address:** [Your Business Address]
    """)


def show_refund_page():
    """Cancellation & Refund Policy page"""
    st.title("💰 Cancellation & Refund Policy")
    st.markdown("---")
    
    st.markdown("""
    **Last Updated:** January 2025
    
    ## 1. CANCELLATION POLICY
    
    ### How to Cancel:
    - Login to your account
    - Go to Settings → Subscription
    - Click "Cancel Subscription"
    - Confirm cancellation
    
    ### What Happens After Cancellation:
    - Access continues until end of current billing period
    - No further charges
    - Data retained for 30 days
    - Can reactivate anytime
    
    ## 2. REFUND POLICY
    
    ### Eligible for Refund:
    - Within 7 days of billing
    - Service not used or minimal usage
    - Technical issues preventing service use
    
    ### Refund Amount:
    - Pro-rated based on days remaining in billing cycle
    - Original payment method
    - Processed within 7-10 business days
    
    ### NOT Eligible for Refund:
    - After 7 days of billing
    - Violation of terms of service
    - Account suspension for abuse
    - Partial month usage
    
    ## 3. REFUND PROCESS
    
    1. Email refund request to: refunds@omnicomni.ai
    2. Include:
       - Account email
       - Reason for refund
       - Transaction ID
    3. We review within 48 hours
    4. Approved refunds processed within 7-10 days
    
    ## 4. ENTERPRISE PLAN CANCELLATION
    
    - Requires 30 days written notice
    - Pro-rated refund for unused months
    - Custom contracts may have different terms
    
    ## 5. FAILED PAYMENTS
    
    - Service suspended after 7 days
    - Account deleted after 30 days
    - No refund for suspended period
    
    ## 6. CONTACT
    
    For refund inquiries:
    
    **Email:** refunds@omnicomni.ai  
    **Support:** support@omnicomni.ai  
    **Response Time:** 24-48 hours
    """)


def show_contact_page():
    """Contact Us page"""
    st.title("📞 Contact Us")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 Email Support")
        st.markdown("""
        **General Inquiries:**  
        support@omnicomni.ai
        
        **Billing & Refunds:**  
        billing@omnicomni.ai
        
        **Technical Support:**  
        tech@omnicomni.ai
        
        **Legal & Privacy:**  
        legal@omnicomni.ai
        """)
    
    with col2:
        st.subheader("🏢 Business Information")
        st.markdown("""
        **Company:** OmniComni AI  
        **Website:** https://omnicomni.ai
        
        **Business Hours:**  
        Monday - Friday: 9 AM - 6 PM IST  
        Saturday: 10 AM - 4 PM IST  
        Sunday: Closed
        
        **Enterprise Support:** 24/7
        """)
    
    st.markdown("---")
    
    st.subheader("💬 Send us a Message")
    
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        subject = st.selectbox("Subject", [
            "General Inquiry",
            "Technical Support",
            "Billing Question",
            "Refund Request",
            "Enterprise Plan",
            "Other"
        ])
        message = st.text_area("Message", height=150)
        
        if st.form_submit_button("Send Message"):
            if name and email and message:
                st.success("✅ Message sent! We'll respond within 24 hours.")
                # TODO: Implement email sending
            else:
                st.error("Please fill in all fields")
