"""
Reservations page for ToolShare application.
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.services import ToolService, ReservationService, ReviewService
from lib.auth import require_login, get_current_user
from lib.storage import display_image
from datetime import date
import os

def render_reservation_card(reservation, is_borrower=True):
    """Render a reservation card."""
    with st.container():
        # Header with status badge
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if is_borrower:
                st.markdown(f"### 🔧 {reservation['tool_title']}")
                st.write(f"**Owner:** {reservation['owner_name']} (@{reservation['owner_username']})")
            else:
                st.markdown(f"### 🔧 {reservation['tool_title']}")
                st.write(f"**Borrower:** {reservation['borrower_name']} (@{reservation['borrower_username']})")
        
        with col2:
            status = reservation['status']
            if status == 'requested':
                st.warning("⏳ Pending")
            elif status == 'accepted':
                st.success("✅ Approved")
            elif status == 'declined':
                st.error("❌ Declined")
            elif status == 'cancelled':
                st.info("🚫 Cancelled")
            elif status == 'completed':
                st.info("✅ Completed")
        
        # Dates and details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Start Date:** {reservation['start_date']}")
        with col2:
            st.write(f"**End Date:** {reservation['end_date']}")
        with col3:
            st.write(f"**Requested:** {reservation['created_at'][:10]}")
        
        # Actions based on status and role
        if status == 'requested' and is_borrower:
            if st.button(f"Cancel Request", key=f"cancel_{reservation['id']}", 
                       type="secondary", use_container_width=True):
                current_user = get_current_user()
                if current_user and ReservationService.update_reservation_status(
                    reservation['id'], current_user['id'], 'cancelled'
                ):
                    st.success("Reservation cancelled.")
                    st.rerun()
                else:
                    st.error("Failed to cancel reservation.")
        
        elif status == 'requested' and not is_borrower:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"✅ Approve", key=f"approve_{reservation['id']}", 
                           type="primary", use_container_width=True):
                    current_user = get_current_user()
                    if not current_user:
                        st.error("Unable to get user information. Please try logging in again.")
                        return
                    if ReservationService.update_reservation_status(
                        reservation['id'], current_user['id'], 'accepted'
                    ):
                        st.success("Reservation approved!")
                        st.rerun()
                    else:
                        st.error("Failed to approve. May conflict with other bookings.")
            
            with col2:
                if st.button(f"❌ Decline", key=f"decline_{reservation['id']}", 
                           type="secondary", use_container_width=True):
                    current_user = get_current_user()
                    if not current_user:
                        st.error("Unable to get user information. Please try logging in again.")
                        return
                    if ReservationService.update_reservation_status(
                        reservation['id'], current_user['id'], 'declined'
                    ):
                        st.success("Reservation declined.")
                        st.rerun()
                    else:
                        st.error("Failed to decline reservation.")
        
        elif status == 'accepted' and is_borrower:
            if st.button(f"Cancel Reservation", key=f"cancel_{reservation['id']}", 
                       type="secondary", use_container_width=True):
                current_user = get_current_user()
                if current_user and ReservationService.update_reservation_status(
                    reservation['id'], current_user['id'], 'cancelled'
                ):
                    st.success("Reservation cancelled.")
                    st.rerun()
                else:
                    st.error("Failed to cancel reservation.")
        
        elif status == 'completed':
            # Check if user can leave a review
            current_user = get_current_user()
            if current_user and ReviewService.can_review(reservation['id'], current_user['id']):
                if st.button(f"⭐ Leave Review", key=f"review_{reservation['id']}", 
                           type="primary", use_container_width=True):
                    st.session_state.review_reservation_id = reservation['id']
                    st.rerun()
            else:
                st.info("Review already submitted or not eligible")

def render_review_form(reservation_id):
    """Render review form for a completed reservation."""
    reservation = ReservationService.get_reservation(reservation_id)
    if not reservation:
        st.error("Reservation not found")
        return
    
    st.subheader(f"⭐ Review: {reservation['tool_title']}")
    
    with st.form("review_form"):
        rating = st.slider("Rating", 1, 5, 5, help="1 = Poor, 5 = Excellent")
        comment = st.text_area("Comment (Optional)", 
                             placeholder="Share your experience with this tool...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("Submit Review", use_container_width=True, type="primary")
        
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if submit:
            current_user = get_current_user()
            if not current_user:
                st.error("Unable to get user information. Please try logging in again.")
                return
            review_id = ReviewService.create_review(
                reservation_id, current_user['id'], rating, comment
            )
            
            if review_id:
                st.success("Review submitted successfully!")
                if 'review_reservation_id' in st.session_state:
                    del st.session_state.review_reservation_id
                st.rerun()
            else:
                st.error("Failed to submit review.")
        
        if cancel:
            if 'review_reservation_id' in st.session_state:
                del st.session_state.review_reservation_id
            st.rerun()

def main():
    """Main reservations page function."""
    st.set_page_config(
        page_title="ToolShare - Reservations",
        page_icon="📅",
        layout="wide"
    )
    
    # Require login
    require_login()
    current_user = get_current_user()
    
    if not current_user:
        st.error("Unable to get user information. Please try logging in again.")
        st.stop()
    
    # Navigation
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("home.py")
    
    with col2:
        if st.button("🔍 Browse", use_container_width=True):
            st.switch_page("pages/browse.py")
    
    with col3:
        if st.button("➕ Add Tool", use_container_width=True):
            st.switch_page("pages/add_tool.py")
    
    with col4:
        if st.button("🔧 My Tools", use_container_width=True):
            st.switch_page("pages/my_tools.py")
    
    with col5:
        if st.button("📅 Reservations", use_container_width=True, disabled=True):
            pass  # Current page
    
    with col6:
        current_user = get_current_user()
        if current_user:
            if st.button(f"👤 {current_user['full_name']}", use_container_width=True):
                st.switch_page("pages/profile.py")
        else:
            if st.button("🔑 Account", use_container_width=True):
                st.switch_page("pages/login.py")
    
    # Handle review form
    if 'review_reservation_id' in st.session_state:
        render_review_form(st.session_state.review_reservation_id)
        return
    
    st.title("📅 My Reservations")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📤 My Requests", "📥 Incoming Requests"])
    
    with tab1:
        st.subheader("Tools I Want to Borrow")
        
        # Get user's reservations as borrower
        borrower_reservations = ReservationService.get_user_reservations(
            current_user['id'], as_borrower=True
        )
        
        if not borrower_reservations:
            st.info("You haven't requested any tools yet.")
            if st.button("🔍 Browse Available Tools", use_container_width=True):
                st.switch_page("pages/browse.py")
        else:
            # Group by status
            requested = [r for r in borrower_reservations if r['status'] == 'requested']
            accepted = [r for r in borrower_reservations if r['status'] == 'accepted']
            completed = [r for r in borrower_reservations if r['status'] == 'completed']
            declined = [r for r in borrower_reservations if r['status'] == 'declined']
            cancelled = [r for r in borrower_reservations if r['status'] == 'cancelled']
            
            # Display sections
            if requested:
                st.markdown("### ⏳ Pending Approval")
                for reservation in requested:
                    render_reservation_card(reservation, is_borrower=True)
                    st.markdown("---")
            
            if accepted:
                st.markdown("### ✅ Approved")
                for reservation in accepted:
                    render_reservation_card(reservation, is_borrower=True)
                    st.markdown("---")
            
            if completed:
                st.markdown("### ✅ Completed")
                for reservation in completed:
                    render_reservation_card(reservation, is_borrower=True)
                    st.markdown("---")
            
            if declined or cancelled:
                with st.expander("📜 History (Declined/Cancelled)"):
                    for reservation in declined + cancelled:
                        render_reservation_card(reservation, is_borrower=True)
                        st.markdown("---")
    
    with tab2:
        st.subheader("Requests for My Tools")
        
        # Get reservations for user's tools
        owner_reservations = ReservationService.get_user_reservations(
            current_user['id'], as_borrower=False
        )
        
        if not owner_reservations:
            st.info("No one has requested your tools yet.")
            if st.button("➕ Add a Tool to Share", use_container_width=True):
                st.switch_page("pages/add_tool.py")
        else:
            # Group by status
            requested = [r for r in owner_reservations if r['status'] == 'requested']
            accepted = [r for r in owner_reservations if r['status'] == 'accepted']
            completed = [r for r in owner_reservations if r['status'] == 'completed']
            declined = [r for r in owner_reservations if r['status'] == 'declined']
            cancelled = [r for r in owner_reservations if r['status'] == 'cancelled']
            
            # Display sections
            if requested:
                st.markdown("### ⏳ Awaiting Your Response")
                for reservation in requested:
                    render_reservation_card(reservation, is_borrower=False)
                    st.markdown("---")
            
            if accepted:
                st.markdown("### ✅ Approved Rentals")
                for reservation in accepted:
                    render_reservation_card(reservation, is_borrower=False)
                    st.markdown("---")
            
            if completed:
                st.markdown("### ✅ Completed Rentals")
                for reservation in completed:
                    render_reservation_card(reservation, is_borrower=False)
                    st.markdown("---")
            
            if declined or cancelled:
                with st.expander("📜 History (Declined/Cancelled)"):
                    for reservation in declined + cancelled:
                        render_reservation_card(reservation, is_borrower=False)
                        st.markdown("---")

if __name__ == "__main__":
    main()