"""
Add/Edit tool page for ToolShare application.
"""
import streamlit as st
from lib.services import ToolService
from lib.auth import require_login, get_current_user
from lib.storage import save_tool_images

CATEGORIES = [
    "Power Tools", "Hand Tools", "Garden Tools", "Automotive", 
    "Kitchen Appliances", "Cleaning", "Sports Equipment", 
    "Electronics", "Home Improvement", "Other"
]

CONDITIONS = ["new", "good", "fair"]

def render_tool_form(tool=None, is_edit=False):
    """Render tool creation/edit form."""
    st.subheader("📝 Tool Information")
    
    with st.form("tool_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Tool Name*", 
                value=tool['title'] if tool else "",
                placeholder="e.g., Electric Drill, Lawn Mower"
            )
            
            category = st.selectbox(
                "Category*", 
                CATEGORIES,
                index=CATEGORIES.index(tool['category']) if tool and tool['category'] in CATEGORIES else 0
            )
        
        with col2:
            condition = st.selectbox(
                "Condition*", 
                CONDITIONS,
                index=CONDITIONS.index(tool['condition']) if tool else 1,
                format_func=lambda x: x.title()
            )
        
        description = st.text_area(
            "Description*", 
            value=tool['description'] if tool else "",
            placeholder="Describe the tool, its features, and any special instructions...",
            height=100
        )
        
        # Image upload
        st.subheader("📷 Images")
        uploaded_files = st.file_uploader(
            "Upload tool images",
            type=['jpg', 'jpeg', 'png', 'gif'],
            accept_multiple_files=True,
            help="Upload up to 5 images. First image will be used as the main photo."
        )
        
        if tool and tool.get('image_paths'):
            st.write("**Current Images:**")
            for i, img_path in enumerate(tool['image_paths']):
                st.write(f"{i+1}. {img_path}")
        
        submit_text = "Update Tool" if is_edit else "Add Tool"
        submit = st.form_submit_button(submit_text, use_container_width=True)
        
        if submit:
            # Validation
            if not title or not description:
                st.error("Please fill in all required fields")
                return False
            
            if len(title) < 3:
                st.error("Tool name must be at least 3 characters long")
                return False
            
            if len(description) < 10:
                st.error("Description must be at least 10 characters long")
                return False
            
            # Handle image uploads
            image_paths = []
            if uploaded_files:
                if len(uploaded_files) > 5:
                    st.error("Maximum 5 images allowed")
                    return False
                
                with st.spinner("Uploading images..."):
                    image_paths = save_tool_images(uploaded_files)
                    
                if not image_paths:
                    st.error("Failed to upload images. Please try again.")
                    return False
            elif tool and tool.get('image_paths'):
                # Keep existing images if no new ones uploaded
                image_paths = tool['image_paths']
            
            current_user = get_current_user()
            
            if is_edit and tool:
                # Update existing tool
                success = ToolService.update_tool(
                    tool['id'],
                    current_user['id'],
                    title,
                    description,
                    category,
                    condition,
                    image_paths
                )
                
                if success:
                    st.success("Tool updated successfully!")
                    st.balloons()
                    
                    if st.button("View Tool"):
                        st.session_state.selected_tool_id = tool['id']
                        st.switch_page("app/tool_detail.py")
                else:
                    st.error("Failed to update tool. You may not have permission.")
            else:
                # Create new tool
                tool_id = ToolService.create_tool(
                    current_user['id'],
                    title,
                    description,
                    category,
                    condition,
                    image_paths
                )
                
                if tool_id:
                    st.success("Tool added successfully!")
                    st.balloons()
                    
                    if st.button("View Tool"):
                        st.session_state.selected_tool_id = tool_id
                        st.switch_page("app/tool_detail.py")
                else:
                    st.error("Failed to add tool. Please try again.")
            
            return True
    
    return False

def main():
    """Main add/edit tool page function."""
    st.set_page_config(
        page_title="ToolShare - Add Tool",
        page_icon="➕",
        layout="wide"
    )
    
    # Require login
    require_login()
    
    # Check if editing existing tool
    tool_id = st.session_state.get('edit_tool_id')
    tool = None
    is_edit = False
    
    if tool_id:
        tool = ToolService.get_tool(tool_id)
        current_user = get_current_user()
        
        if not tool:
            st.error("Tool not found")
            if st.button("My Tools"):
                st.switch_page("app/my_tools.py")
            return
        
        if tool['owner_id'] != current_user['id']:
            st.error("You don't have permission to edit this tool")
            if st.button("My Tools"):
                st.switch_page("app/my_tools.py")
            return
        
        is_edit = True
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("← Back"):
            if is_edit:
                st.switch_page("app/my_tools.py")
            else:
                st.switch_page("app/home.py")
    
    with col2:
        if st.button("🏠 Home"):
            st.switch_page("app/home.py")
    
    # Page title
    if is_edit:
        st.title(f"✏️ Edit Tool: {tool['title']}")
    else:
        st.title("➕ Add New Tool")
        st.write("Share your tools with the community!")
    
    # Tool form
    render_tool_form(tool, is_edit)
    
    # Clear edit state after form submission
    if 'edit_tool_id' in st.session_state and st.session_state.get('form_submitted'):
        del st.session_state.edit_tool_id
        del st.session_state.form_submitted

if __name__ == "__main__":
    main()