"""Login page for ToolShare."""

import streamlit as st

from lib.supabase_client import get_supabase_client, sync_user_data


def main():
    st.title("🔐 Login to ToolShare")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        submitted = st.form_submit_button("Login")

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return

            try:
                supabase = get_supabase_client()
                result = supabase.auth.sign_in_with_password({"email": email, "password": password})

                if result.user:
                    st.session_state.user = result.user
                    sync_user_data(result.user)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

            except Exception as e:
                st.error(f"Login failed: {str(e)}")

    st.markdown("---")
    st.info("Don't have an account? Use the sidebar to sign up!")


if __name__ == "__main__":
    main()
