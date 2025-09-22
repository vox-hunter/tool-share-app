"""My Tools page for ToolShare."""

import streamlit as st

from lib.models import ReservationStatus
from lib.services import ReservationService, StorageService, ToolService
from lib.supabase_client import get_current_user, require_auth


def main():
    require_auth()
    current_user = get_current_user()

    st.title("🔧 My Tools")

    try:
        # Get user's tools
        tools = ToolService.get_tools({"owner_id": current_user.id})

        if not tools:
            st.info("You haven't listed any tools yet.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add Your First Tool", type="primary"):
                    st.session_state.navigation = "Add Tool"
                    st.rerun()

            with col2:
                if st.button("🔍 Browse Tools to Get Ideas"):
                    st.session_state.navigation = "Browse Tools"
                    st.rerun()

            return

        # Tool management tabs
        tab1, tab2 = st.tabs(["📋 My Tool Listings", "📊 Tool Performance"])

        with tab1:
            st.markdown(f"**You have {len(tools)} tool(s) listed**")

            # Display tools
            for tool in tools:
                display_tool_management_card(tool, current_user.id)

        with tab2:
            display_tool_analytics(tools, current_user.id)

    except Exception as e:
        st.error(f"Error loading your tools: {str(e)}")


def display_tool_management_card(tool, user_id):
    """Display a tool management card."""
    with st.expander(f"🔧 {tool.title}", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            # Tool details
            st.write(f"**Category:** {tool.category}")
            st.write(f"**Condition:** {tool.condition.value.title()}")

            if tool.daily_price > 0:
                st.write(f"**Daily Price:** ${tool.daily_price:.2f}")
            else:
                st.write("**Price:** Free")

            st.write(f"**Status:** {'🟢 Active' if tool.is_active else '🔴 Inactive'}")

            if tool.description:
                st.write("**Description:**")
                st.write(tool.description[:200] + ("..." if len(tool.description) > 200 else ""))

        with col2:
            # Tool image
            if tool.images:
                try:
                    image_url = StorageService.get_public_url(tool.images[0])
                    st.image(image_url, width=150)
                except:
                    st.image("https://via.placeholder.com/150x100?text=No+Image", width=150)
            else:
                st.image("https://via.placeholder.com/150x100?text=No+Image", width=150)

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("✏️ Edit", key=f"edit_{tool.id}"):
                st.session_state.edit_tool_id = tool.id
                st.session_state.show_edit_form = True
                st.rerun()

        with col2:
            status_text = "🔴 Deactivate" if tool.is_active else "🟢 Activate"
            if st.button(status_text, key=f"toggle_{tool.id}"):
                toggle_tool_status(tool.id, not tool.is_active)

        with col3:
            if st.button("📋 Reservations", key=f"reservations_{tool.id}"):
                st.session_state.view_tool_reservations = tool.id
                st.rerun()

        with col4:
            if st.button("🗑️ Delete", key=f"delete_{tool.id}"):
                if st.session_state.get(f"confirm_delete_{tool.id}", False):
                    delete_tool(tool.id)
                else:
                    st.session_state[f"confirm_delete_{tool.id}"] = True
                    st.rerun()

        # Show confirmation for delete
        if st.session_state.get(f"confirm_delete_{tool.id}", False):
            st.warning(
                "⚠️ Are you sure you want to delete this tool? This action cannot be undone."
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete", key=f"confirm_yes_{tool.id}"):
                    delete_tool(tool.id)
            with col2:
                if st.button("Cancel", key=f"confirm_no_{tool.id}"):
                    del st.session_state[f"confirm_delete_{tool.id}"]
                    st.rerun()

        # Show reservations for this tool
        if st.session_state.get("view_tool_reservations") == tool.id:
            show_tool_reservations(tool)


def toggle_tool_status(tool_id, new_status):
    """Toggle tool active status."""
    try:
        ToolService.update_tool(tool_id, {"is_active": new_status})
        status_text = "activated" if new_status else "deactivated"
        st.success(f"Tool {status_text} successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to update tool: {str(e)}")


def delete_tool(tool_id):
    """Delete a tool."""
    try:
        ToolService.delete_tool(tool_id)
        st.success("Tool deleted successfully!")
        # Clear any related session state
        for key in list(st.session_state.keys()):
            if tool_id in key:
                del st.session_state[key]
        st.rerun()
    except Exception as e:
        st.error(f"Failed to delete tool: {str(e)}")


def show_tool_reservations(tool):
    """Show reservations for a specific tool."""
    st.subheader(f"📋 Reservations for {tool.title}")

    try:
        # Get reservations for this tool
        reservations = ReservationService.get_reservations(tool.owner_id, role="owner")
        tool_reservations = [r for r in reservations if r.tool_id == tool.id]

        if not tool_reservations:
            st.info("No reservations yet for this tool.")
            return

        # Group by status
        requested = [r for r in tool_reservations if r.status == ReservationStatus.REQUESTED]
        accepted = [r for r in tool_reservations if r.status == ReservationStatus.ACCEPTED]
        other = [
            r
            for r in tool_reservations
            if r.status not in [ReservationStatus.REQUESTED, ReservationStatus.ACCEPTED]
        ]

        # Pending requests (need action)
        if requested:
            st.markdown("### 🕐 Pending Requests")
            for reservation in requested:
                display_reservation_card(reservation, is_owner=True)

        # Accepted reservations
        if accepted:
            st.markdown("### ✅ Accepted Reservations")
            for reservation in accepted:
                display_reservation_card(reservation, is_owner=True)

        # Other reservations
        if other:
            st.markdown("### 📜 Past Reservations")
            for reservation in other:
                display_reservation_card(reservation, is_owner=True)

    except Exception as e:
        st.error(f"Error loading reservations: {str(e)}")

    # Close button
    if st.button("❌ Close Reservations", key=f"close_reservations_{tool.id}"):
        del st.session_state["view_tool_reservations"]
        st.rerun()


def display_reservation_card(reservation, is_owner=False):
    """Display a reservation card."""
    with st.container():
        # Status badge
        status_colors = {
            "requested": "#ffa500",
            "accepted": "#28a745",
            "declined": "#dc3545",
            "cancelled": "#6c757d",
            "completed": "#17a2b8",
        }

        status_color = status_colors.get(reservation.status.value, "#6c757d")

        st.markdown(
            f"""
        <div style="padding: 1rem; border-left: 4px solid {status_color}; background-color: #f8f9fa; margin-bottom: 1rem;">
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            if reservation.borrower:
                st.write(
                    f"**Borrower:** {reservation.borrower.full_name or reservation.borrower.email}"
                )

            st.write(f"**Dates:** {reservation.start_date} to {reservation.end_date}")
            st.write(f"**Status:** {reservation.status.value.title()}")

            # Calculate rental duration
            duration = (reservation.end_date - reservation.start_date).days + 1
            st.write(f"**Duration:** {duration} day(s)")

        with col2:
            # Action buttons for owner
            if is_owner and reservation.status == ReservationStatus.REQUESTED:
                if st.button("✅ Accept", key=f"accept_{reservation.id}"):
                    update_reservation_status(reservation.id, ReservationStatus.ACCEPTED)

                if st.button("❌ Decline", key=f"decline_{reservation.id}"):
                    update_reservation_status(reservation.id, ReservationStatus.DECLINED)

        st.markdown("</div>", unsafe_allow_html=True)


def update_reservation_status(reservation_id, status):
    """Update reservation status."""
    try:
        current_user = get_current_user()
        ReservationService.update_reservation_status(reservation_id, status, current_user.id)
        st.success(f"Reservation {status.value}!")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to update reservation: {str(e)}")


def display_tool_analytics(tools, user_id):
    """Display analytics for user's tools."""
    st.markdown("### 📊 Your Tool Sharing Statistics")

    try:
        # Get all reservations for user's tools
        all_reservations = ReservationService.get_reservations(user_id, role="owner")

        # Calculate metrics
        total_requests = len(all_reservations)
        accepted_requests = len(
            [r for r in all_reservations if r.status == ReservationStatus.ACCEPTED]
        )
        completed_requests = len(
            [r for r in all_reservations if r.status == ReservationStatus.COMPLETED]
        )
        pending_requests = len(
            [r for r in all_reservations if r.status == ReservationStatus.REQUESTED]
        )

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Requests", total_requests)

        with col2:
            st.metric("Accepted", accepted_requests)

        with col3:
            st.metric("Completed", completed_requests)

        with col4:
            st.metric("Pending", pending_requests)

        # Most popular tools
        if all_reservations:
            st.markdown("### 🏆 Most Popular Tools")

            tool_popularity = {}
            for reservation in all_reservations:
                tool_id = reservation.tool_id
                tool_name = reservation.tool.title if reservation.tool else "Unknown Tool"

                if tool_id not in tool_popularity:
                    tool_popularity[tool_id] = {"name": tool_name, "count": 0}
                tool_popularity[tool_id]["count"] += 1

            # Sort by popularity
            sorted_tools = sorted(tool_popularity.values(), key=lambda x: x["count"], reverse=True)

            for i, tool_data in enumerate(sorted_tools[:5], 1):
                st.write(f"{i}. **{tool_data['name']}** - {tool_data['count']} requests")

        else:
            st.info("No reservation data available yet. Start sharing your tools to see analytics!")

    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")


if __name__ == "__main__":
    main()
