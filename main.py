"""Main ToolShare Streamlit application."""

import importlib.util
import os
import sys

import streamlit as st

from lib.supabase_client import get_current_user, init_auth_state, logout

# Page configuration
st.set_page_config(
    page_title="ToolShare", page_icon="🛠️", layout="wide", initial_sidebar_state="expanded"
)

# Initialize authentication
init_auth_state()

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .status-badge {
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .status-requested { background-color: #ffa500; }
    .status-accepted { background-color: #28a745; }
    .status-declined { background-color: #dc3545; }
    .status-cancelled { background-color: #6c757d; }
    .status-completed { background-color: #17a2b8; }
</style>
""",
    unsafe_allow_html=True,
)


def load_page(page_name):
    """Dynamically load a page module."""
    page_path = f"app/{page_name}.py"
    if os.path.exists(page_path):
        spec = importlib.util.spec_from_file_location(page_name, page_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[page_name] = module
        spec.loader.exec_module(module)
        return module
    return None


def main():
    """Main application logic."""
    current_user = get_current_user()

    # Header
    st.markdown('<h1 class="main-header">🛠️ ToolShare</h1>', unsafe_allow_html=True)

    # Navigation
    if current_user:
        # Authenticated navigation
        with st.sidebar:
            st.success(f"Welcome, {current_user.email}!")

            page = st.selectbox(
                "Navigate to:",
                [
                    "Home",
                    "Browse Tools",
                    "My Tools",
                    "Add Tool",
                    "Reservations",
                    "Profile",
                    "Admin",
                ],
                key="navigation",
            )

            if st.button("Logout"):
                logout()

        # Load selected page
        page_mapping = {
            "Home": "home",
            "Browse Tools": "browse",
            "My Tools": "my_tools",
            "Add Tool": "add_tool",
            "Reservations": "reservations",
            "Profile": "profile",
            "Admin": "admin",
        }

        page_module = load_page(page_mapping.get(page, "home"))
        if page_module and hasattr(page_module, "main"):
            page_module.main()
        else:
            st.error(f"Page '{page}' not found or has no main function.")

    else:
        # Unauthenticated navigation
        with st.sidebar:
            auth_option = st.selectbox("Choose an option:", ["Login", "Sign Up", "Browse Tools"])

        if auth_option == "Login":
            page_module = load_page("login")
        elif auth_option == "Sign Up":
            page_module = load_page("signup")
        else:
            page_module = load_page("browse")

        if page_module and hasattr(page_module, "main"):
            page_module.main()
        else:
            # Fallback home page for unauthenticated users
            st.markdown(
                """
            ## Welcome to ToolShare! 🛠️

            A community platform for sharing tools and equipment with your neighbors.

            ### Why ToolShare?
            - 💰 **Save Money**: Borrow instead of buying expensive tools
            - 🌱 **Go Green**: Reduce waste through sharing
            - 🤝 **Build Community**: Connect with neighbors
            - 🔧 **Access More Tools**: Use tools you wouldn't normally own

            ### Get Started
            1. **Sign up** for a free account
            2. **Browse** available tools in your area
            3. **Request** to borrow what you need
            4. **Share** your own tools to help others

            Please sign up or log in to get started!
            """
            )


if __name__ == "__main__":
    main()
