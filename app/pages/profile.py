"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Profile page for ToolShare application.
"""
import streamlit as st
from lib.auth import require_login, get_current_user, update_user_profile, logout
from lib.services import ReviewService
from lib.storage import save_avatar, display_image
import os

def render_profile_form(user):
    """Render profile edit form."""
    st.subheader("✏️ Edit Profile")
    
    with st.form("profile_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Current Avatar:**")
            if user['avatar_path'] and os.path.exists(user['avatar_path']):
                display_image(user['avatar_path'], width=150)
            else:
                st.write("No avatar uploaded")
            
            # Avatar upload
            uploaded_avatar = st.file_uploader(
                "Upload New Avatar",
                type=['jpg', 'jpeg', 'png'],
                help="Upload a profile picture (optional)"
            )
        
        with col2:
            full_name = st.text_input("Full Name", value=user['full_name'])
            bio = st.text_area(
                "Bio",
                value=user['bio'] or "",
                placeholder="Tell the community about yourself, your interests, or what tools you have...",
                height=150
            )
        
        submit = st.form_submit_button("Update Profile", use_container_width=True, type="primary")
        
        if submit:
            if not full_name:
                st.error("Full name is required")
                return False
            
            # Handle avatar upload
            avatar_path = user['avatar_path']
            if uploaded_avatar:
                new_avatar_path = save_avatar(uploaded_avatar)
                if new_avatar_path:
                    avatar_path = new_avatar_path
                else:
                    st.error("Failed to upload avatar")
                    return False
            
            # Update profile
            if update_user_profile(user['id'], full_name, bio, avatar_path):
                st.success("Profile updated successfully!")
                st.balloons()
                # Update session state
                updated_user = get_current_user()
                st.session_state.user_data = updated_user
                st.rerun()
            else:
                st.error("Failed to update profile")
            
            return True
    
    return False

def render_user_reviews(user_id):
    """Render reviews about the user."""
    st.subheader("⭐ Reviews from Others")
    
    reviews = ReviewService.get_user_reviews(user_id)
    
    if not reviews:
        st.info("No reviews yet. Start sharing tools to get reviews!")
        return
    
    # Calculate average rating
    avg_rating = ReviewService.get_user_rating(user_id)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
    with col2:
        st.metric("Total Reviews", len(reviews))
    
    st.markdown("---")
    
    # Display reviews
    for review in reviews:
        with st.container():
            # Rating stars
            stars = "⭐" * review['rating'] + "☆" * (5 - review['rating'])
            st.write(f"**{stars} ({review['rating']}/5)**")
            
            # Review content
            st.write(f"**Tool:** {review['tool_title']}")
            if review['comment']:
                st.write(f"*\"{review['comment']}\"*")
            
            st.write(f"**By:** {review['reviewer_name']} • {review['created_at'][:10]}")
            
            st.markdown("---")

def render_user_stats(user):
    """Render user statistics."""
    st.subheader("📊 Your Stats")
    
    # Get user's tools and reviews
    from lib.services import ToolService, ReservationService
    
    tools = ToolService.get_tools(owner_id=user['id'], active_only=False)
    active_tools = [t for t in tools if t['is_active']]
    
    borrower_reservations = ReservationService.get_user_reservations(user['id'], as_borrower=True)
    owner_reservations = ReservationService.get_user_reservations(user['id'], as_borrower=False)
    
    completed_borrows = len([r for r in borrower_reservations if r['status'] == 'completed'])
    completed_lends = len([r for r in owner_reservations if r['status'] == 'completed'])
    
    avg_rating = ReviewService.get_user_rating(user['id'])
    
    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Tools", len(active_tools))
    
    with col2:
        st.metric("Tools Borrowed", completed_borrows)
    
    with col3:
        st.metric("Tools Lent", completed_lends)
    
    with col4:
        if avg_rating > 0:
            st.metric("Rating", f"{avg_rating:.1f}⭐")
        else:
            st.metric("Rating", "No ratings yet")

def render_account_settings(user):
    """Render account settings section."""
    st.subheader("⚙️ Account Settings")
    
    # Basic account info (read-only)
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Member Since:** {user['created_at'][:10]}")
    
    with col2:
        st.write(f"**User ID:** {user['id']}")
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        logout()
        st.success("You have been logged out.")
        st.switch_page("app/home.py")

def main():
    """Main profile page function."""
    st.set_page_config(
        page_title="ToolShare - Profile",
        page_icon="👤",
        layout="wide"
    )
    
    # Require login
    require_login()
    current_user = get_current_user()
    
    # Navigation
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app/home.py")
    
    with col2:
        if st.button("🔍 Browse", use_container_width=True):
            st.switch_page("pages/browse.py")
    
    with col3:
        if st.button("🔧 My Tools", use_container_width=True):
            st.switch_page("pages/my_tools.py")
    
    with col4:
        if st.button("📅 Reservations", use_container_width=True):
            st.switch_page("pages/reservations.py")
    
    with col5:
        if st.button("👤 Profile", use_container_width=True, disabled=True):
            pass  # Current page
    
    # Page header
    st.title(f"👤 {current_user['full_name']}")
    st.write(f"@{current_user['username']}")
    
    # Profile sections in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✏️ Edit Profile", "📊 Stats", "⭐ Reviews", "⚙️ Settings"])
    
    with tab1:
        render_profile_form(current_user)
    
    with tab2:
        render_user_stats(current_user)
    
    with tab3:
        render_user_reviews(current_user['id'])
    
    with tab4:
        render_account_settings(current_user)

if __name__ == "__main__":
    main()