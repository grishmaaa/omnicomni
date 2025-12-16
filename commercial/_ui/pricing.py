"""
Pricing Page

Display subscription tiers and upgrade options
"""

import streamlit as st
from subscription import SUBSCRIPTION_TIERS, format_price, get_tier_info

def show_pricing_page():
    """Display pricing page with subscription tiers"""
    
    st.markdown("""
    <style>
    .pricing-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    
    .pricing-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        border: 3px solid transparent;
        transition: all 0.3s;
    }
    
    .pricing-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    }
    
    .pricing-card.featured {
        border-color: #667eea;
        transform: scale(1.05);
    }
    
    .tier-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    .tier-price {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
        margin: 1rem 0;
    }
    
    .tier-period {
        color: #718096;
        font-size: 1rem;
    }
    
    .feature-list {
        text-align: left;
        margin: 2rem 0;
    }
    
    .feature-item {
        padding: 0.5rem 0;
        color: #4a5568;
    }
    
    .feature-item::before {
        content: "✓ ";
        color: #48bb78;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .popular-badge {
        background: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="pricing-header">
        <h1>Choose Your Plan</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Start free, upgrade when you need more
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    # Free Tier
    with col1:
        tier_info = get_tier_info('free')
        st.markdown(f"""
        <div class="pricing-card">
            <div class="tier-name">{tier_info['name']}</div>
            <div class="tier-price">$0</div>
            <div class="tier-period">forever</div>
            <div class="feature-list">
        """, unsafe_allow_html=True)
        
        for feature in tier_info['features']:
            st.markdown(f'<div class="feature-item">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if st.button("Get Started", key="free_btn", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()
    
    # Pro Tier (Featured)
    with col2:
        tier_info = get_tier_info('pro')
        st.markdown(f"""
        <div class="pricing-card featured">
            <div class="popular-badge">MOST POPULAR</div>
            <div class="tier-name">{tier_info['name']}</div>
            <div class="tier-price">{format_price(tier_info['price'])}</div>
            <div class="tier-period">per month</div>
            <div class="feature-list">
        """, unsafe_allow_html=True)
        
        for feature in tier_info['features']:
            st.markdown(f'<div class="feature-item">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if st.button("Upgrade to Pro", key="pro_btn", type="primary", use_container_width=True):
            st.info("🚧 Payment integration coming soon! Contact support to upgrade.")
    
    # Enterprise Tier
    with col3:
        tier_info = get_tier_info('enterprise')
        st.markdown(f"""
        <div class="pricing-card">
            <div class="tier-name">{tier_info['name']}</div>
            <div class="tier-price">{format_price(tier_info['price'])}</div>
            <div class="tier-period">per month</div>
            <div class="feature-list">
        """, unsafe_allow_html=True)
        
        for feature in tier_info['features']:
            st.markdown(f'<div class="feature-item">{feature}</div>', unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if st.button("Contact Sales", key="enterprise_btn", use_container_width=True):
            st.info("📧 Contact: sales@aivideogen.com for Enterprise pricing")
    
    st.markdown("---")
    
    # FAQ Section
    st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem 0;'>Frequently Asked Questions</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("❓ Can I change my plan later?"):
            st.write("Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.")
        
        with st.expander("❓ What happens if I exceed my limit?"):
            st.write("You'll be prompted to upgrade to continue generating videos. Your existing videos remain accessible.")
        
        with st.expander("❓ Do you offer refunds?"):
            st.write("We offer a 30-day money-back guarantee for all paid plans, no questions asked.")
    
    with col2:
        with st.expander("❓ Can I cancel anytime?"):
            st.write("Yes, you can cancel your subscription at any time. You'll retain access until the end of your billing period.")
        
        with st.expander("❓ What payment methods do you accept?"):
            st.write("We accept all major credit cards, debit cards, and PayPal through Stripe.")
        
        with st.expander("❓ Is there a free trial for paid plans?"):
            st.write("Start with the Free plan to test the platform. Upgrade when you're ready for more features.")
    
    st.markdown("---")
    
    # Back button
    if st.button("← Back to Home", use_container_width=False):
        st.session_state.page = "landing"
        st.rerun()


if __name__ == "__main__":
    st.set_page_config(
        page_title="Pricing - AI Video Generator",
        page_icon="💰",
        layout="wide"
    )
    show_pricing_page()
