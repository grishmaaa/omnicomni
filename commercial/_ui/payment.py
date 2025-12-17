"""
Payment and Billing UI Pages
"""

import streamlit as st
from datetime import datetime
from payment import (
    create_checkout_session, get_user_payments, 
    get_user_invoices, init_payment_tables
)


def show_payment_page(user_db):
    """Show payment/subscription selection page"""
    st.title("💳 Choose Your Plan")
    st.markdown("---")
    
    # Pricing tiers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🌟 Starter")
        st.markdown("### $9.99/month")
        st.markdown("""
        - 10 videos per month
        - HD quality (720p)
        - Basic support
        - Watermark included
        """)
        if st.button("Select Starter", key="starter", use_container_width=True):
            st.session_state.selected_plan = "starter"
            st.session_state.selected_price = 999  # cents
            st.rerun()
    
    with col2:
        st.subheader("⭐ Professional")
        st.markdown("### $29.99/month")
        st.markdown("""
        - 50 videos per month
        - Full HD quality (1080p)
        - Priority support
        - No watermark
        """)
        if st.button("Select Professional", key="pro", type="primary", use_container_width=True):
            st.session_state.selected_plan = "professional"
            st.session_state.selected_price = 2999
            st.rerun()
    
    with col3:
        st.subheader("🚀 Enterprise")
        st.markdown("### $99.99/month")
        st.markdown("""
        - Unlimited videos
        - 4K quality
        - 24/7 dedicated support
        - API access
        - Custom branding
        """)
        if st.button("Select Enterprise", key="enterprise", use_container_width=True):
            st.session_state.selected_plan = "enterprise"
            st.session_state.selected_price = 9999
            st.rerun()
    
    # Show checkout if plan selected
    if 'selected_plan' in st.session_state:
        st.markdown("---")
        st.subheader(f"✅ Selected: {st.session_state.selected_plan.title()}")
        st.write(f"**Amount:** ${st.session_state.selected_price / 100:.2f}/month")
        
        if st.button("Proceed to Payment", type="primary", use_container_width=True):
            try:
                # Create Stripe checkout session
                # Note: You'll need to create price IDs in Stripe dashboard
                price_ids = {
                    'starter': 'price_starter_id',  # Replace with actual Stripe price ID
                    'professional': 'price_pro_id',
                    'enterprise': 'price_enterprise_id'
                }
                
                checkout_url = create_checkout_session(
                    price_id=price_ids[st.session_state.selected_plan],
                    user_email=st.session_state.user['email'],
                    user_id=st.session_state.user['uid'],
                    success_url="https://your-app.streamlit.app/?payment=success",
                    cancel_url="https://your-app.streamlit.app/?payment=cancelled"
                )
                
                st.markdown(f"[Click here to complete payment]({checkout_url})")
                st.info("You'll be redirected to Stripe's secure payment page")
            except Exception as e:
                st.error(f"Payment setup failed: {e}")


def show_billing_page(user_db):
    """Show billing history and invoices"""
    st.title("📄 Billing & Invoices")
    st.markdown("---")
    
    # Payment History
    st.subheader("💰 Payment History")
    
    try:
        payments = get_user_payments(user_db['id'])
        
        if payments:
            for payment in payments:
                with st.expander(f"Payment #{payment['id']} - ${payment['amount']:.2f} - {payment['created_at'].strftime('%Y-%m-%d')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Amount:** ${payment['amount']:.2f}")
                        st.write(f"**Status:** {payment['status'].title()}")
                    with col2:
                        st.write(f"**Date:** {payment['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Transaction ID:** {payment['payment_intent_id']}")
        else:
            st.info("No payment history yet")
    except Exception as e:
        st.error(f"Failed to load payment history: {e}")
    
    st.markdown("---")
    
    # Invoices
    st.subheader("🧾 Invoices")
    
    try:
        invoices = get_user_invoices(user_db['id'])
        
        if invoices:
            for invoice in invoices:
                with st.expander(f"Invoice #{invoice['id']} - ${invoice['total']:.2f} - {invoice['created_at'].strftime('%Y-%m-%d')}"):
                    st.write(f"**Total:** ${invoice['total']:.2f}")
                    st.write(f"**Date:** {invoice['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Payment ID:** {invoice['payment_id']}")
                    
                    if st.button(f"Download Invoice #{invoice['id']}", key=f"download_{invoice['id']}"):
                        # Generate PDF invoice (implement later)
                        st.info("Invoice download feature coming soon")
        else:
            st.info("No invoices yet")
    except Exception as e:
        st.error(f"Failed to load invoices: {e}")


def check_payment_required(user_db) -> bool:
    """
    Check if user needs to pay before using the service
    
    Returns:
        bool: True if payment is required, False if user has active subscription
    """
    try:
        # Check if user has any successful payments
        payments = get_user_payments(user_db['id'])
        
        # If user has at least one successful payment, allow access
        if payments and any(p['status'] == 'completed' for p in payments):
            return False
        
        # Otherwise, payment is required
        return True
    except:
        # If there's an error, require payment to be safe
        return True
