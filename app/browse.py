"""Browse tools page for ToolShare."""

import streamlit as st

from lib.models import TOOL_CATEGORIES
from lib.services import StorageService, ToolService
from lib.supabase_client import get_current_user


def main():
    st.title("🔍 Browse Tools")

    # Filters
    with st.expander("🔧 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            search_term = st.text_input("🔎 Search", placeholder="Search tools...")

        with col2:
            category_filter = st.selectbox("📂 Category", ["All Categories"] + TOOL_CATEGORIES)

        with col3:
            sort_option = st.selectbox(
                "📊 Sort by",
                ["Newest First", "Oldest First", "Price: Low to High", "Price: High to Low"],
            )

    # Apply filters
    filters = {}
    if search_term:
        filters["search"] = search_term
    if category_filter != "All Categories":
        filters["category"] = category_filter

    try:
        # Get tools
        tools = ToolService.get_tools(filters)

        # Apply sorting (basic implementation)
        if sort_option == "Oldest First":
            tools = sorted(tools, key=lambda x: x.created_at or "")
        elif sort_option == "Price: Low to High":
            tools = sorted(tools, key=lambda x: x.daily_price)
        elif sort_option == "Price: High to Low":
            tools = sorted(tools, key=lambda x: x.daily_price, reverse=True)
        # "Newest First" is default from database query

        # Results summary
        st.markdown(f"**Found {len(tools)} tools**")

        if tools:
            # Display tools in grid
            cols_per_row = 2
            for i in range(0, len(tools), cols_per_row):
                cols = st.columns(cols_per_row)

                for j, tool in enumerate(tools[i : i + cols_per_row]):
                    with cols[j]:
                        display_tool_card(tool)
        else:
            st.info("No tools found matching your criteria. Try adjusting your filters!")

            # Suggest adding a tool if user is logged in
            current_user = get_current_user()
            if current_user:
                st.markdown("### Be the first to add a tool in this category!")
                if st.button("Add a Tool", key="add_tool_suggestion"):
                    st.session_state.navigation = "Add Tool"
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading tools: {str(e)}")


def display_tool_card(tool):
    """Display a tool card."""
    with st.container():
        # Add some custom styling
        st.markdown('<div class="tool-card">', unsafe_allow_html=True)

        # Tool image
        if tool.images:
            try:
                image_url = StorageService.get_public_url(tool.images[0])
                st.image(image_url, use_column_width=True, caption=tool.title)
            except Exception:
                st.image(
                    "https://via.placeholder.com/300x200?text=No+Image",
                    use_column_width=True,
                    caption=tool.title,
                )
        else:
            st.image(
                "https://via.placeholder.com/300x200?text=No+Image",
                use_column_width=True,
                caption=tool.title,
            )

        # Tool details
        st.subheader(tool.title)

        # Category and condition
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Category:** {tool.category}")
        with col2:
            st.write(f"**Condition:** {tool.condition.value.title()}")

        # Description
        if tool.description:
            description = tool.description[:150]
            if len(tool.description) > 150:
                description += "..."
            st.write(description)

        # Owner info
        owner_name = "Anonymous"
        if tool.owner and tool.owner.full_name:
            owner_name = tool.owner.full_name
        st.write(f"**Owner:** {owner_name}")

        # Price
        if tool.daily_price > 0:
            st.write(f"**Price:** ${tool.daily_price:.2f}/day")
        else:
            st.write("**Price:** Free")

        # Location (if available)
        if tool.latitude and tool.longitude:
            st.write("📍 Location available")

        # Action buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("View Details", key=f"view_{tool.id}"):
                # Store tool ID in session state and navigate to tool detail
                st.session_state.selected_tool_id = tool.id
                st.session_state.show_tool_detail = True
                st.rerun()

        with col2:
            current_user = get_current_user()
            if current_user and current_user.id != tool.owner_id:
                if st.button("Reserve", key=f"reserve_{tool.id}", type="primary"):
                    st.session_state.selected_tool_id = tool.id
                    st.session_state.show_reservation_form = True
                    st.rerun()
            elif current_user and current_user.id == tool.owner_id:
                st.write("*Your tool*")
            else:
                st.info("Login to reserve")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")


# Handle tool detail modal
if st.session_state.get("show_tool_detail", False):
    show_tool_detail_modal()

# Handle reservation form modal
if st.session_state.get("show_reservation_form", False):
    show_reservation_form_modal()


def show_tool_detail_modal():
    """Show tool detail in a modal-like expander."""
    tool_id = st.session_state.get("selected_tool_id")

    if tool_id:
        try:
            # Get tool details (this is a simplified approach)
            tools = ToolService.get_tools()
            tool = next((t for t in tools if t.id == tool_id), None)

            if tool:
                with st.expander("🔍 Tool Details", expanded=True):
                    # Close button
                    if st.button("❌ Close", key="close_detail"):
                        st.session_state.show_tool_detail = False
                        st.rerun()

                    # Tool images
                    if tool.images:
                        for i, image_path in enumerate(tool.images):
                            try:
                                image_url = StorageService.get_public_url(image_path)
                                st.image(image_url, caption=f"Image {i+1}", use_column_width=True)
                            except Exception:
                                st.image(
                                    "https://via.placeholder.com/400x300?text=Image+Not+Found",
                                    caption=f"Image {i+1}",
                                )

                    # Full details
                    st.title(tool.title)
                    st.write(f"**Category:** {tool.category}")
                    st.write(f"**Condition:** {tool.condition.value.title()}")

                    if tool.description:
                        st.write("**Description:**")
                        st.write(tool.description)

                    # Owner details
                    if tool.owner:
                        st.write(f"**Owner:** {tool.owner.full_name or 'Anonymous'}")
                        if tool.owner.bio:
                            st.write(f"**About Owner:** {tool.owner.bio}")

                    # Price
                    if tool.daily_price > 0:
                        st.write(f"**Daily Rate:** ${tool.daily_price:.2f}")
                    else:
                        st.write("**Price:** Free")

                    # Location
                    if tool.latitude and tool.longitude:
                        st.write(f"**Location:** {tool.latitude:.4f}, {tool.longitude:.4f}")

                    # Reserve button
                    current_user = get_current_user()
                    if current_user and current_user.id != tool.owner_id:
                        if st.button("📅 Make Reservation", key="reserve_detail", type="primary"):
                            st.session_state.show_reservation_form = True
                            st.session_state.show_tool_detail = False
                            st.rerun()
                    elif current_user and current_user.id == tool.owner_id:
                        st.info("This is your tool.")
                    else:
                        st.warning("Please log in to make a reservation.")

        except Exception as e:
            st.error(f"Error loading tool details: {str(e)}")


def show_reservation_form_modal():
    """Show reservation form in a modal-like expander."""
    tool_id = st.session_state.get("selected_tool_id")
    current_user = get_current_user()

    if tool_id and current_user:
        with st.expander("📅 Make Reservation", expanded=True):
            # Close button
            if st.button("❌ Close", key="close_reservation"):
                st.session_state.show_reservation_form = False
                st.rerun()

            st.write("Select your desired rental dates:")

            with st.form("reservation_form"):
                col1, col2 = st.columns(2)

                with col1:
                    start_date = st.date_input("Start Date")

                with col2:
                    end_date = st.date_input("End Date")

                message = st.text_area(
                    "Message to Owner (Optional)",
                    placeholder="Let the owner know how you plan to use the tool...",
                )

                submitted = st.form_submit_button("Submit Request", type="primary")

                if submitted:
                    try:
                        from datetime import date

                        from lib.services import ReservationService

                        # Validate dates
                        if start_date < date.today():
                            st.error("Start date cannot be in the past.")
                        elif end_date < start_date:
                            st.error("End date must be after start date.")
                        else:
                            # Create reservation
                            reservation = ReservationService.create_reservation(
                                tool_id=tool_id,
                                borrower_id=current_user.id,
                                start_date=start_date,
                                end_date=end_date,
                            )

                            st.success("Reservation request submitted successfully!")
                            st.info("The tool owner will review your request and respond soon.")

                            # Clear the form
                            st.session_state.show_reservation_form = False
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to create reservation: {str(e)}")


# Handle tool detail modal
if st.session_state.get("show_tool_detail", False):
    show_tool_detail_modal()

# Handle reservation form modal
if st.session_state.get("show_reservation_form", False):
    show_reservation_form_modal()


def show_tool_detail_modal():
    """Show tool detail in a modal-like expander."""
    tool_id = st.session_state.get("selected_tool_id")

    if tool_id:
        try:
            # Get tool details (this is a simplified approach)
            tools = ToolService.get_tools()
            tool = next((t for t in tools if t.id == tool_id), None)

            if tool:
                with st.expander("🔍 Tool Details", expanded=True):
                    # Close button
                    if st.button("❌ Close", key="close_detail"):
                        st.session_state.show_tool_detail = False
                        st.rerun()

                    # Tool images
                    if tool.images:
                        for i, image_path in enumerate(tool.images):
                            try:
                                image_url = StorageService.get_public_url(image_path)
                                st.image(image_url, caption=f"Image {i+1}", use_column_width=True)
                            except Exception:
                                st.image(
                                    "https://via.placeholder.com/400x300?text=Image+Not+Found",
                                    caption=f"Image {i+1}",
                                )

                    # Full details
                    st.title(tool.title)
                    st.write(f"**Category:** {tool.category}")
                    st.write(f"**Condition:** {tool.condition.value.title()}")

                    if tool.description:
                        st.write("**Description:**")
                        st.write(tool.description)

                    # Owner details
                    if tool.owner:
                        st.write(f"**Owner:** {tool.owner.full_name or 'Anonymous'}")
                        if tool.owner.bio:
                            st.write(f"**About Owner:** {tool.owner.bio}")

                    # Price
                    if tool.daily_price > 0:
                        st.write(f"**Daily Rate:** ${tool.daily_price:.2f}")
                    else:
                        st.write("**Price:** Free")

                    # Location
                    if tool.latitude and tool.longitude:
                        st.write(f"**Location:** {tool.latitude:.4f}, {tool.longitude:.4f}")

                    # Reserve button
                    current_user = get_current_user()
                    if current_user and current_user.id != tool.owner_id:
                        if st.button("📅 Make Reservation", key="reserve_detail", type="primary"):
                            st.session_state.show_reservation_form = True
                            st.session_state.show_tool_detail = False
                            st.rerun()
                    elif current_user and current_user.id == tool.owner_id:
                        st.info("This is your tool.")
                    else:
                        st.warning("Please log in to make a reservation.")

        except Exception as e:
            st.error(f"Error loading tool details: {str(e)}")


def show_reservation_form_modal():
    """Show reservation form in a modal-like expander."""
    tool_id = st.session_state.get("selected_tool_id")
    current_user = get_current_user()

    if tool_id and current_user:
        with st.expander("📅 Make Reservation", expanded=True):
            # Close button
            if st.button("❌ Close", key="close_reservation"):
                st.session_state.show_reservation_form = False
                st.rerun()

            st.write("Select your desired rental dates:")

            with st.form("reservation_form"):
                col1, col2 = st.columns(2)

                with col1:
                    start_date = st.date_input("Start Date")

                with col2:
                    end_date = st.date_input("End Date")

                st.text_area(
                    "Message to Owner (Optional)",
                    placeholder="Let the owner know how you plan to use the tool...",
                )

                submitted = st.form_submit_button("Submit Request", type="primary")

                if submitted:
                    try:
                        from datetime import date

                        from lib.services import ReservationService

                        # Validate dates
                        if start_date < date.today():
                            st.error("Start date cannot be in the past.")
                        elif end_date < start_date:
                            st.error("End date must be after start date.")
                        else:
                            # Create reservation
                            ReservationService.create_reservation(
                                tool_id=tool_id,
                                borrower_id=current_user.id,
                                start_date=start_date,
                                end_date=end_date,
                            )

                            st.success("Reservation request submitted successfully!")
                            st.info("The tool owner will review your request and respond soon.")

                            # Clear the form
                            st.session_state.show_reservation_form = False
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to create reservation: {str(e)}")


if __name__ == "__main__":
    main()
