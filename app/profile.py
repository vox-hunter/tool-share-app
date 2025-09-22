"""User profile page for ToolShare."""

import streamlit as st

from lib.services import UserService
from lib.supabase_client import get_current_user, require_auth


def main():
    require_auth()
    current_user = get_current_user()

    st.title("👤 My Profile")

    # Get user data from database
    try:
        user_data = UserService.get_user_by_id(current_user.id)
        if not user_data:
            st.error("User data not found.")
            return
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        return

    # Profile form
    with st.form("profile_form"):
        st.subheader("📝 Profile Information")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Avatar section
            st.markdown("**Profile Picture**")

            if user_data.avatar_url:
                try:
                    st.image(user_data.avatar_url, width=150, caption="Current avatar")
                except:
                    st.image("https://via.placeholder.com/150x150?text=No+Avatar", width=150)
            else:
                st.image("https://via.placeholder.com/150x150?text=No+Avatar", width=150)

            # Avatar upload
            uploaded_avatar = st.file_uploader(
                "Upload new profile picture",
                type=["png", "jpg", "jpeg"],
                help="Square images work best",
            )

        with col2:
            # Personal information
            full_name = st.text_input(
                "Full Name*", value=user_data.full_name or "", placeholder="Enter your full name"
            )

            email = st.text_input(
                "Email", value=user_data.email, disabled=True, help="Email cannot be changed"
            )

            bio = st.text_area(
                "Bio",
                value=user_data.bio or "",
                placeholder="Tell others about yourself, your interests, or tools you're looking for...",
                max_chars=500,
                help="This helps other community members get to know you",
            )

        # Account statistics
        st.subheader("📊 Account Statistics")

        col1, col2, col3 = st.columns(3)

        with col1:
            if user_data.created_at:
                join_date = user_data.created_at.strftime("%B %Y")
                st.write(f"**Joined:** {join_date}")
            else:
                st.write("**Joined:** Recently")

        with col2:
            # TODO: Calculate actual stats
            st.write("**Tools Shared:** 0")

        with col3:
            st.write("**Reputation:** ⭐⭐⭐⭐⭐")

        # Submit button
        submitted = st.form_submit_button("💾 Update Profile", type="primary")

        if submitted:
            # Validation
            if not full_name:
                st.error("Full name is required.")
                return

            try:
                update_data = {"full_name": full_name.strip(), "bio": bio.strip() if bio else None}

                # Handle avatar upload
                if uploaded_avatar:
                    avatar_url = upload_avatar(uploaded_avatar, current_user.id)
                    if avatar_url:
                        update_data["avatar_url"] = avatar_url

                # Update profile
                with st.spinner("Updating profile..."):
                    UserService.update_user(current_user.id, update_data)

                    st.success("✅ Profile updated successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"Failed to update profile: {str(e)}")

    st.markdown("---")

    # Account actions
    st.subheader("⚙️ Account Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Privacy Settings**")
        show_email = st.checkbox("Show email to other users", value=False, disabled=True)
        show_location = st.checkbox("Share approximate location", value=False, disabled=True)
        st.info("Privacy settings coming soon!")

    with col2:
        st.markdown("**Notifications**")
        email_notifications = st.checkbox("Email notifications", value=True, disabled=True)
        reservation_updates = st.checkbox("Reservation updates", value=True, disabled=True)
        st.info("Notification preferences coming soon!")

    # Danger zone
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")

    with st.expander("Account Management", expanded=False):
        st.warning("These actions are irreversible!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Reset Password", disabled=True):
                st.info("Password reset coming soon!")

        with col2:
            if st.button("🗑️ Delete Account", disabled=True):
                st.info("Account deletion coming soon!")


def upload_avatar(uploaded_file, user_id):
    """Upload user avatar."""
    try:
        # Generate filename
        file_extension = uploaded_file.name.split(".")[-1]
        filename = f"avatar.{file_extension}"

        # For now, we'll use a simple placeholder return
        # In a real implementation, you'd upload to Supabase storage
        st.info("Avatar upload functionality coming soon!")
        return None

    except Exception as e:
        st.error(f"Failed to upload avatar: {str(e)}")
        return None


def get_user_statistics(user_id):
    """Get user statistics."""
    # TODO: Implement actual statistics gathering
    return {
        "tools_shared": 0,
        "successful_rentals": 0,
        "reviews_received": 0,
        "average_rating": 0.0,
    }


if __name__ == "__main__":
    main()
