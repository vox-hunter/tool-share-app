"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

My Tools page for ToolShare application.
"""
import streamlit as st
from lib.services import ToolService, ReservationService
from lib.auth import require_login, get_current_user
from lib.storage import display_image
import os

def render_tool_card(tool):
    """Render a tool card with management options."""
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Tool image
            if tool['image_paths']:
                image_path = tool['image_paths'][0]
                if os.path.exists(image_path):
                    st.image(image_path, width=150)
                else:
                    st.write("📷 No image")
            else:
                st.write("📷 No image")
        
        with col2:
            # Tool info
            st.markdown(f"### {tool['title']}")
            st.write(f"**Category:** {tool['category']}")
            st.write(f"**Condition:** {tool['condition'].title()}")
            
            # Status badge
            if tool['is_active']:
                st.success("✅ Active")
            else:
                st.warning("⚠️ Inactive")
            
            # Description (truncated)
            description = tool['description']
            if len(description) > 80:
                description = description[:80] + "..."
            st.write(description)
            
            # Action buttons
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button("👁️ View", key=f"view_{tool['id']}", use_container_width=True):
                    st.session_state.selected_tool_id = tool['id']
                    st.switch_page("pages/tool_detail.py")
            
            with col_btn2:
                if st.button("✏️ Edit", key=f"edit_{tool['id']}", use_container_width=True):
                    st.session_state.edit_tool_id = tool['id']
                    st.switch_page("pages/add_tool.py")
            
            with col_btn3:
                if st.button("📋 Requests", key=f"requests_{tool['id']}", use_container_width=True):
                    st.session_state.selected_tool_id = tool['id']
                    st.session_state.show_tool_requests = True
                    st.rerun()
            
            with col_btn4:
                if tool['is_active']:
                    if st.button("🗑️ Delete", key=f"delete_{tool['id']}", 
                               use_container_width=True, type="secondary"):
                        st.session_state.confirm_delete_tool_id = tool['id']
                        st.rerun()

def render_tool_requests(tool_id, tool_title):
    """Render reservation requests for a specific tool."""
    st.subheader(f"📋 Reservation Requests for: {tool_title}")
    
    current_user = get_current_user()
    reservations = ReservationService.get_user_reservations(current_user['id'], as_borrower=False)
    
    # Filter for this specific tool
    tool_reservations = [r for r in reservations if r['tool_id'] == tool_id]
    
    if not tool_reservations:
        st.info("No reservation requests for this tool yet.")
        return
    
    for reservation in tool_reservations:
        with st.expander(f"{reservation['status'].title()} - {reservation['borrower_name']} ({reservation['start_date']} to {reservation['end_date']})"):
            st.write(f"**Borrower:** {reservation['borrower_name']} (@{reservation['borrower_username']})")
            st.write(f"**Dates:** {reservation['start_date']} to {reservation['end_date']}")
            st.write(f"**Status:** {reservation['status'].title()}")
            st.write(f"**Requested:** {reservation['created_at'][:16]}")
            
            if reservation['status'] == 'requested':
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{reservation['id']}", 
                               use_container_width=True, type="primary"):
                        if ReservationService.update_reservation_status(
                            reservation['id'], current_user['id'], 'accepted'
                        ):
                            st.success("Reservation approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve reservation. May conflict with other bookings.")
                
                with col2:
                    if st.button(f"❌ Decline", key=f"decline_{reservation['id']}", 
                               use_container_width=True, type="secondary"):
                        if ReservationService.update_reservation_status(
                            reservation['id'], current_user['id'], 'declined'
                        ):
                            st.success("Reservation declined.")
                            st.rerun()
                        else:
                            st.error("Failed to decline reservation.")
    
    if st.button("← Back to My Tools"):
        if 'show_tool_requests' in st.session_state:
            del st.session_state.show_tool_requests
        if 'selected_tool_id' in st.session_state:
            del st.session_state.selected_tool_id
        st.rerun()

def render_delete_confirmation(tool_id):
    """Render delete confirmation dialog."""
    tool = ToolService.get_tool(tool_id)
    if not tool:
        return
    
    st.error(f"⚠️ Are you sure you want to delete '{tool['title']}'?")
    st.write("This action cannot be undone. If there are active reservations, the tool will be deactivated instead.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Yes, Delete", use_container_width=True, type="primary"):
            current_user = get_current_user()
            if ToolService.delete_tool(tool_id, current_user['id']):
                st.success("Tool deleted successfully!")
                if 'confirm_delete_tool_id' in st.session_state:
                    del st.session_state.confirm_delete_tool_id
                st.rerun()
            else:
                st.error("Failed to delete tool.")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            if 'confirm_delete_tool_id' in st.session_state:
                del st.session_state.confirm_delete_tool_id
            st.rerun()

def main():
    """Main my tools page function."""
    st.set_page_config(
        page_title="ToolShare - My Tools",
        page_icon="🔧",
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
        if st.button("➕ Add Tool", use_container_width=True):
            st.switch_page("pages/add_tool.py")
    
    with col4:
        if st.button("🔧 My Tools", use_container_width=True, disabled=True):
            pass  # Current page
    
    with col5:
        if st.button("📅 Reservations", use_container_width=True):
            st.switch_page("pages/reservations.py")
    
    # Handle delete confirmation
    if 'confirm_delete_tool_id' in st.session_state:
        render_delete_confirmation(st.session_state.confirm_delete_tool_id)
        return
    
    # Handle tool requests view
    if st.session_state.get('show_tool_requests') and 'selected_tool_id' in st.session_state:
        tool_id = st.session_state.selected_tool_id
        tool = ToolService.get_tool(tool_id)
        if tool:
            render_tool_requests(tool_id, tool['title'])
        return
    
    st.title("🔧 My Tools")
    
    # Get user's tools
    tools = ToolService.get_tools(owner_id=current_user['id'], active_only=False)
    
    if not tools:
        st.info("You haven't added any tools yet.")
        if st.button("➕ Add Your First Tool", use_container_width=True, type="primary"):
            st.switch_page("pages/add_tool.py")
        return
    
    # Statistics
    active_tools = len([t for t in tools if t['is_active']])
    inactive_tools = len(tools) - active_tools
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tools", len(tools))
    with col2:
        st.metric("Active Tools", active_tools)
    with col3:
        st.metric("Inactive Tools", inactive_tools)
    
    st.markdown("---")
    
    # Display tools
    for tool in tools:
        render_tool_card(tool)
        st.markdown("---")

if __name__ == "__main__":
    main()