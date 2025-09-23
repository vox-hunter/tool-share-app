"""
Login page for ToolShare application.
"""
import streamlit as st
from lib.auth import authenticate_user, is_logged_in

def main():
    """Main login page function."""
    st.set_page_config(
        page_title="ToolShare - Login",
        page_icon="🛠️"
    )
    
    # Redirect if already logged in
    if is_logged_in():
        st.success("You are already logged in!")
        if st.button("Go to Home"):
            st.switch_page("app/home.py")
        return
    
    st.title("🔐 Login to ToolShare")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            user = authenticate_user(username, password)
            if user:
                # Store user info in session state
                st.session_state.user_id = user['id']
                st.session_state.username = user['username']
                st.session_state.user_data = user
                
                st.success(f"Welcome back, {user['full_name']}!")
                st.balloons()
                
                # Add a delay before redirect
                st.write("Redirecting to home page...")
                st.switch_page("app/home.py")
            else:
                st.error("Invalid username or password")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("app/home.py")
    
    with col2:
        if st.button("Don't have an account? Sign Up", use_container_width=True):
            st.switch_page("app/signup.py")

if __name__ == "__main__":
    main()