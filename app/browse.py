"""
Browse tools page for ToolShare application.
"""
import streamlit as st
from lib.services import ToolService
from lib.storage import display_image
import os

def render_filters():
    """Render search and filter options."""
    st.subheader("🔍 Search & Filter")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get search term from session state if coming from home page
        default_search = st.session_state.get('search_term', '')
        search = st.text_input("Search tools", value=default_search, placeholder="e.g., drill, ladder, bike")
        # Clear search term from session state after using it
        if 'search_term' in st.session_state:
            del st.session_state.search_term
    
    with col2:
        categories = ["All"] + ToolService.get_categories()
        category = st.selectbox("Category", categories)
        category = None if category == "All" else category
    
    return search, category

def render_tool_card(tool):
    """Render a single tool card."""
    with st.container():
        # Tool image
        if tool['image_paths']:
            image_path = tool['image_paths'][0]
            if os.path.exists(image_path):
                st.image(image_path, width=250)
            else:
                st.write("📷 No image available")
        else:
            st.write("📷 No image available")
        
        # Tool info
        st.markdown(f"### {tool['title']}")
        st.write(f"**Category:** {tool['category']}")
        st.write(f"**Condition:** {tool['condition'].title()}")
        st.write(f"**Owner:** {tool['full_name']}")
        
        # Description (truncated)
        description = tool['description']
        if len(description) > 100:
            description = description[:100] + "..."
        st.write(description)
        
        # View details button
        if st.button(f"View Details", key=f"view_{tool['id']}", use_container_width=True):
            st.session_state.selected_tool_id = tool['id']
            st.switch_page("app/tool_detail.py")

def render_tools_grid(tools):
    """Render tools in a grid layout."""
    if not tools:
        st.info("No tools found matching your criteria. Try adjusting your search or filters.")
        return
    
    st.write(f"Found {len(tools)} tool(s)")
    
    # Display tools in grid (3 columns)
    cols = st.columns(3)
    
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            render_tool_card(tool)

def main():
    """Main browse page function."""
    st.set_page_config(
        page_title="ToolShare - Browse Tools",
        page_icon="🔍",
        layout="wide"
    )
    
    # Navigation
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app/home.py")
    
    with col2:
        if st.button("🔍 Browse", use_container_width=True, disabled=True):
            pass  # Current page
    
    with col3:
        if st.button("➕ Add Tool", use_container_width=True):
            st.switch_page("app/add_tool.py")
    
    with col4:
        if st.button("🔧 My Tools", use_container_width=True):
            st.switch_page("app/my_tools.py")
    
    with col5:
        if st.button("📅 Reservations", use_container_width=True):
            st.switch_page("app/reservations.py")
    
    st.title("🔍 Browse Available Tools")
    
    # Filters
    search, category = render_filters()
    
    # Get tools based on filters
    tools = ToolService.get_tools(
        category=category,
        search=search,
        active_only=True
    )
    
    st.markdown("---")
    
    # Display tools
    render_tools_grid(tools)

if __name__ == "__main__":
    main()