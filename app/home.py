"""
Home page for ToolShare application.
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.auth import is_logged_in, get_current_user, logout
from lib.services import ToolService

def render_navigation():
    """Render main navigation."""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("home.py")
    
    with col2:
        if st.button("🔍 Browse", use_container_width=True):
            st.switch_page("pages/browse.py")
    
    with col3:
        if st.button("➕ Add Tool", use_container_width=True):
            if not is_logged_in():
                st.error("Please log in to add tools")
            else:
                st.switch_page("pages/add_tool.py")
    
    with col4:
        if st.button("🔧 My Tools", use_container_width=True):
            if not is_logged_in():
                st.error("Please log in to view your tools")
            else:
                st.switch_page("pages/my_tools.py")
    
    with col5:
        if st.button("📅 Reservations", use_container_width=True):
            if not is_logged_in():
                st.error("Please log in to view reservations")
            else:
                st.switch_page("pages/reservations.py")
    
    with col6:
        if is_logged_in():
            user = get_current_user()
            if user:
                if st.button(f"👤 {user['full_name']}", use_container_width=True):
                    st.switch_page("pages/profile.py")
        else:
            if st.button("🔑 Account", use_container_width=True):
                st.switch_page("pages/login.py")

def render_hero_section():
    """Render hero section with app description."""
    st.markdown("""
    # 🛠️ ToolShare
    
    **Share tools, build community, save money!**
    
    Connect with your neighbors to borrow and lend tools, equipment, and more. 
    Why buy something you'll only use once when you can share?
    
    ---
    """)

def render_featured_tools():
    """Render featured tools section."""
    st.subheader("🌟 Featured Tools")
    
    # Get recent tools
    tools = ToolService.get_tools()[:6]  # Show first 6 tools
    
    if not tools:
        st.info("No tools available yet. Be the first to add one!")
        return
    
    # Display tools in cards
    cols = st.columns(3)
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"**{tool['title']}**")
                st.write(f"Category: {tool['category']}")
                st.write(f"Owner: {tool['full_name']}")
                st.write(f"Condition: {tool['condition'].title()}")
                
                # Display first image if available
                if tool['image_paths']:
                    image_path = tool['image_paths'][0]
                    if os.path.exists(image_path):
                        st.image(image_path, width=200)
                
                if st.button("View Details", key=f"view_{tool['id']}"):
                    st.session_state.selected_tool_id = tool['id']
                    st.switch_page("pages/tool_detail.py")

def render_quick_search():
    """Render quick search section."""
    st.subheader("🔍 Quick Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Search for tools...", placeholder="e.g., drill, ladder, bike")
    
    with col2:
        if st.button("Search", use_container_width=True):
            if search_term:
                st.session_state.search_term = search_term
                st.switch_page("pages/browse.py")

def render_stats():
    """Render app statistics."""
    # This could show community stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Available Tools", len(ToolService.get_tools()))
    
    with col2:
        st.metric("Categories", len(ToolService.get_categories()))
    
    with col3:
        st.metric("Active Users", "🎯")

def main():
    """Main home page function."""
    st.set_page_config(
        page_title="ToolShare - Home",
        page_icon="🛠️",
        layout="wide"
    )
    
    render_navigation()
    render_hero_section()
    render_quick_search()
    render_featured_tools()
    
    st.markdown("---")
    render_stats()
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 2rem;'>
        <p>🌱 ToolShare - Building sustainable communities through sharing</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()