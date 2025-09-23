"""
Sign up page for ToolShare application.
"""
import streamlit as st
from lib.auth import create_user, is_logged_in

def main():
    """Main signup page function."""
    st.set_page_config(
        page_title="ToolShare - Sign Up",
        page_icon="🛠️"
    )
    
    # Redirect if already logged in
    if is_logged_in():
        st.info("You are already logged in!")
        if st.button("Go to Home"):
            st.switch_page("app/home.py")
        return
    
    st.title("📝 Join ToolShare")
    st.write("Create your account to start sharing tools with your community!")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*", help="Choose a unique username")
            full_name = st.text_input("Full Name*", help="Your real name")
        
        with col2:
            password = st.text_input("Password*", type="password", help="Choose a strong password")
            confirm_password = st.text_input("Confirm Password*", type="password")
        
        bio = st.text_area("Bio (Optional)", 
                          placeholder="Tell the community about yourself...",
                          help="Share your interests, skills, or what tools you might have")
        
        submit = st.form_submit_button("Create Account")
        
        if submit:
            # Validation
            if not username or not password or not full_name:
                st.error("Please fill in all required fields")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters long")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            # Create user
            user_id = create_user(username, password, full_name, bio)
            
            if user_id:
                st.success(f"Account created successfully! Welcome to ToolShare, {full_name}!")
                st.balloons()
                
                # Auto-login after signup
                st.session_state.user_id = user_id
                st.session_state.username = username
                
                st.info("You are now logged in. Redirecting to home page...")
                st.switch_page("app/home.py")
            else:
                st.error("Username already exists. Please choose a different username.")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("app/home.py")
    
    with col2:
        if st.button("Already have an account? Login", use_container_width=True):
            st.switch_page("app/login.py")

if __name__ == "__main__":
    main()