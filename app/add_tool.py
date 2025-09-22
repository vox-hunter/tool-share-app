"""Add/Edit tool page for ToolShare."""

import uuid

import streamlit as st

from lib.models import TOOL_CATEGORIES, ToolCondition
from lib.services import StorageService, ToolService
from lib.supabase_client import get_current_user, require_auth


def main():
    require_auth()
    current_user = get_current_user()

    st.title("➕ Add a Tool")

    # Instructions
    st.markdown(
        """
    Share your tools with the community! Fill out the form below to list a tool that others can borrow.
    """
    )

    with st.form("add_tool_form", clear_on_submit=True):
        # Basic information
        st.subheader("🔧 Tool Information")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Tool Title*", placeholder="e.g., Cordless Drill, Lawn Mower")
            category = st.selectbox("Category*", TOOL_CATEGORIES)
            condition = st.selectbox("Condition*", [c.value.title() for c in ToolCondition])

        with col2:
            daily_price = st.number_input(
                "Daily Price ($)",
                min_value=0.0,
                value=0.0,
                step=0.50,
                help="Leave as 0 for free lending",
            )
            location_available = st.checkbox("Share location (optional)")

            # Location inputs (shown conditionally)
            if location_available:
                latitude = st.number_input("Latitude", value=0.0, format="%.6f")
                longitude = st.number_input("Longitude", value=0.0, format="%.6f")
            else:
                latitude = None
                longitude = None

        # Description
        description = st.text_area(
            "Description*",
            placeholder="Describe the tool, its features, condition, and any usage notes...",
            max_chars=1000,
            help="Provide details that will help borrowers understand what they're getting",
        )

        # Image upload
        st.subheader("📸 Images")
        uploaded_files = st.file_uploader(
            "Upload tool images (optional)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            help="Add up to 5 images to showcase your tool",
        )

        # Terms
        st.subheader("📋 Terms & Conditions")
        agree_terms = st.checkbox(
            "I agree to share this tool responsibly and ensure it's in good working condition*"
        )

        # Submit button
        submitted = st.form_submit_button("🚀 List Tool", type="primary")

        if submitted:
            # Validation
            if not title or not category or not description:
                st.error("Please fill in all required fields (marked with *).")
                return

            if not agree_terms:
                st.error("Please agree to the terms and conditions.")
                return

            if uploaded_files and len(uploaded_files) > 5:
                st.error("Maximum 5 images allowed.")
                return

            try:
                # Prepare tool data
                tool_data = {
                    "owner_id": current_user.id,
                    "title": title.strip(),
                    "description": description.strip(),
                    "category": category,
                    "condition": condition.lower(),
                    "daily_price": daily_price,
                    "latitude": latitude,
                    "longitude": longitude,
                    "is_active": True,
                }

                # Create the tool
                with st.spinner("Creating tool listing..."):
                    tool = ToolService.create_tool(tool_data)

                    # Upload images if any
                    if uploaded_files:
                        upload_images(tool.id, uploaded_files)

                    st.success(f"✅ Tool '{title}' has been listed successfully!")
                    st.balloons()

                    # Show next steps
                    st.info("Your tool is now live! Others can browse and request to borrow it.")

                    # Option to view the tool or add another
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View My Tools"):
                            st.session_state.navigation = "My Tools"
                            st.rerun()

                    with col2:
                        if st.button("Add Another Tool"):
                            st.rerun()

            except Exception as e:
                st.error(f"Failed to create tool listing: {str(e)}")

    # Tips section
    st.markdown("---")
    st.markdown(
        """
    ### 💡 Tips for a Great Listing

    **📝 Write a Clear Title**
    Use descriptive titles like "Black & Decker Cordless Drill" instead of just "Drill"

    **📋 Detailed Description**
    Include brand, model, features, and any special instructions

    **📸 Add Quality Photos**
    Show the tool from multiple angles and include any accessories

    **💰 Fair Pricing**
    Research rental rates or consider offering tools for free to build community

    **📍 Location Sharing**
    Sharing your approximate location helps nearby neighbors find your tools
    """
    )


def upload_images(tool_id: str, uploaded_files):
    """Upload images for a tool."""
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # Generate unique filename
            file_extension = uploaded_file.name.split(".")[-1]
            filename = f"{uuid.uuid4()}.{file_extension}"

            # Upload to storage
            StorageService.upload_image(
                file_data=uploaded_file.getvalue(), file_name=filename, tool_id=tool_id
            )

        except Exception as e:
            st.warning(f"Failed to upload {uploaded_file.name}: {str(e)}")


if __name__ == "__main__":
    main()
