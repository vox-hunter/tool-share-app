"""Sign up page for ToolShare."""

import streamlit as st

from lib.supabase_client import get_supabase_client, sync_user_data


def main():
    st.title("📝 Sign Up for ToolShare")

    with st.form("signup_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("Email*", placeholder="Enter your email")
            password = st.text_input("Password*", type="password", placeholder="Create a password")

        with col2:
            full_name = st.text_input("Full Name", placeholder="Enter your full name")
            confirm_password = st.text_input(
                "Confirm Password*", type="password", placeholder="Confirm your password"
            )

        bio = st.text_area(
            "Bio (Optional)", placeholder="Tell others about yourself...", max_chars=500
        )

        submitted = st.form_submit_button("Create Account")

        if submitted:
            # Validation
            if not email or not password or not confirm_password:
                st.error("Please fill in all required fields.")
                return

            if password != confirm_password:
                st.error("Passwords do not match.")
                return

            if len(password) < 6:
                st.error("Password must be at least 6 characters long.")
                return

            try:
                supabase = get_supabase_client()

                # Sign up with Supabase Auth
                result = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                        "options": {"data": {"full_name": full_name, "bio": bio}},
                    }
                )

                if result.user:
                    st.session_state.user = result.user
                    sync_user_data(result.user)

                    st.success("Account created successfully!")

                    # Check if email confirmation is required
                    if not result.session:
                        st.info(
                            "Please check your email to confirm your account before logging in."
                        )
                    else:
                        st.success("You are now logged in!")
                        st.rerun()
                else:
                    st.error("Failed to create account. Please try again.")

            except Exception as e:
                error_msg = str(e)
                if "already registered" in error_msg.lower():
                    st.error(
                        "An account with this email already exists. Please try logging in instead."
                    )
                else:
                    st.error(f"Sign up failed: {error_msg}")

    st.markdown("---")
    st.info("Already have an account? Use the sidebar to log in!")


if __name__ == "__main__":
    main()
