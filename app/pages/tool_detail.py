"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Tool detail page for ToolShare application.
"""
import streamlit as st
from datetime import datetime, date, timedelta
from lib.services import ToolService, ReservationService
from lib.auth import is_logged_in, get_current_user
from lib.storage import display_image_gallery
import os

def render_tool_images(tool):
    """Render tool image gallery."""
    if tool['image_paths']:
        st.subheader("📷 Images")
        display_image_gallery(tool['image_paths'], max_columns=3)
    else:
        st.info("No images available for this tool")

def render_tool_info(tool):
    """Render tool information."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"# {tool['title']}")
        st.write(f"**Category:** {tool['category']}")
        st.write(f"**Condition:** {tool['condition'].title()}")
        
        # Price information
        if tool.get('price', 0) > 0:
            st.write(f"**Price:** ${tool['price']:.2f} per day")
        else:
            st.write("**Price:** Free to borrow")
        
        st.write(f"**Description:**")
        st.write(tool['description'])
    
    with col2:
        st.subheader("👤 Owner")
        
        # Owner avatar
        if tool['avatar_path'] and os.path.exists(tool['avatar_path']):
            st.image(tool['avatar_path'], width=100)
        
        st.write(f"**{tool['full_name']}**")
        st.write(f"@{tool['username']}")
        
        # Contact information
        if tool.get('contact_info'):
            st.write(f"**Contact:** {tool['contact_info']}")
        
        st.write(f"**Member since:** {tool['created_at'][:10]}")

def render_reservation_form(tool):
    """Render reservation request form."""
    if not is_logged_in():
        st.warning("Please log in to reserve this tool")
        if st.button("Login"):
            st.switch_page("pages/login.py")
        return
    
    current_user = get_current_user()
    
    # Check if user data is available
    if not current_user:
        st.error("Unable to get user information. Please try logging in again.")
        return
    
    # Don't allow owner to reserve their own tool
    if current_user['id'] == tool['owner_id']:
        st.info("You cannot reserve your own tool")
        return
    
    st.subheader("📅 Reserve This Tool")
    
    with st.form("reservation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                min_value=date.today(),
                value=date.today()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                min_value=date.today(),
                value=date.today() + timedelta(days=1)
            )
        
        notes = st.text_area("Additional Notes (Optional)", 
                           placeholder="Any specific requirements or questions...")
        
        submit = st.form_submit_button("Request Reservation")
        
        if submit:
            if start_date >= end_date:
                st.error("End date must be after start date")
                return
            
            if start_date < date.today():
                st.error("Start date cannot be in the past")
                return
            
            # Create reservation
            reservation_id = ReservationService.create_reservation(
                tool['id'],
                current_user['id'],
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if reservation_id:
                st.success("Reservation request sent! The tool owner will be notified.")
                st.balloons()
                
                # Show reservation details
                st.info(f"""
                **Reservation Details:**
                - Tool: {tool['title']}
                - Dates: {start_date} to {end_date}
                - Status: Pending approval
                """)
                
                st.session_state.reservation_created = True
            else:
                st.error("Failed to create reservation. The tool may not be available for those dates.")

    # Show "View My Reservations" button outside the form if reservation was created
    if hasattr(st.session_state, 'reservation_created') and st.session_state.reservation_created:
        if st.button("View My Reservations", key="view_reservations"):
            del st.session_state.reservation_created  # Clear the state
            st.switch_page("pages/reservations.py")

def main():
    """Main tool detail page function."""
    st.set_page_config(
        page_title="ToolShare - Tool Details",
        page_icon="🔧",
        layout="wide"
    )
    
    # Get tool ID from session state
    tool_id = st.session_state.get('selected_tool_id')
    
    if not tool_id:
        st.error("No tool selected")
        if st.button("Browse Tools"):
            st.switch_page("pages/browse.py")
        return
    
    # Get tool details
    tool = ToolService.get_tool(tool_id)
    
    if not tool:
        st.error("Tool not found")
        if st.button("Browse Tools"):
            st.switch_page("pages/browse.py")
        return
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("← Back to Browse"):
            st.switch_page("pages/browse.py")
    
    with col2:
        if st.button("🏠 Home"):
            st.switch_page("home.py")
    
    # Tool information
    render_tool_info(tool)
    
    st.markdown("---")
    
    # Tool images
    render_tool_images(tool)
    
    st.markdown("---")
    
    # Reservation form
    render_reservation_form(tool)

if __name__ == "__main__":
    main()