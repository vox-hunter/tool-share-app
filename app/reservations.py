"""Reservations page for ToolShare."""

from datetime import date

import streamlit as st

from lib.models import ReservationStatus
from lib.services import ReservationService, ReviewService
from lib.supabase_client import get_current_user, require_auth


def main():
    require_auth()
    current_user = get_current_user()

    st.title("📅 My Reservations")

    # Tabs for different views
    tab1, tab2 = st.tabs(["📤 My Requests", "📥 Incoming Requests"])

    with tab1:
        show_my_requests(current_user.id)

    with tab2:
        show_incoming_requests(current_user.id)


def show_my_requests(user_id):
    """Show reservations where user is the borrower."""
    st.subheader("Tools I've Requested")

    try:
        reservations = ReservationService.get_reservations(user_id, role="borrower")

        if not reservations:
            st.info("You haven't made any reservation requests yet.")

            if st.button("🔍 Browse Tools to Request"):
                st.session_state.navigation = "Browse Tools"
                st.rerun()
            return

        # Group by status
        pending = [r for r in reservations if r.status == ReservationStatus.REQUESTED]
        upcoming = [
            r
            for r in reservations
            if r.status == ReservationStatus.ACCEPTED and r.start_date >= date.today()
        ]
        current = [
            r
            for r in reservations
            if r.status == ReservationStatus.ACCEPTED and r.start_date <= date.today() <= r.end_date
        ]
        completed = [r for r in reservations if r.status == ReservationStatus.COMPLETED]
        other = [
            r
            for r in reservations
            if r.status in [ReservationStatus.DECLINED, ReservationStatus.CANCELLED]
        ]

        # Pending requests
        if pending:
            st.markdown("### 🕐 Pending Approval")
            for reservation in pending:
                display_borrower_reservation_card(reservation)

        # Current rentals
        if current:
            st.markdown("### 🔄 Currently Borrowed")
            for reservation in current:
                display_borrower_reservation_card(reservation)

        # Upcoming reservations
        if upcoming:
            st.markdown("### 📅 Upcoming Reservations")
            for reservation in upcoming:
                display_borrower_reservation_card(reservation)

        # Completed reservations
        if completed:
            st.markdown("### ✅ Completed")
            for reservation in completed:
                display_borrower_reservation_card(reservation)

        # Declined/Cancelled
        if other:
            st.markdown("### ❌ Declined/Cancelled")
            for reservation in other:
                display_borrower_reservation_card(reservation)

    except Exception as e:
        st.error(f"Error loading your requests: {str(e)}")


def show_incoming_requests(user_id):
    """Show reservations for tools owned by the user."""
    st.subheader("Requests for My Tools")

    try:
        reservations = ReservationService.get_reservations(user_id, role="owner")

        if not reservations:
            st.info("No one has requested your tools yet.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Add a Tool"):
                    st.session_state.navigation = "Add Tool"
                    st.rerun()

            with col2:
                if st.button("🔧 Manage My Tools"):
                    st.session_state.navigation = "My Tools"
                    st.rerun()
            return

        # Group by status
        pending = [r for r in reservations if r.status == ReservationStatus.REQUESTED]
        active = [r for r in reservations if r.status == ReservationStatus.ACCEPTED]
        completed = [r for r in reservations if r.status == ReservationStatus.COMPLETED]
        other = [
            r
            for r in reservations
            if r.status in [ReservationStatus.DECLINED, ReservationStatus.CANCELLED]
        ]

        # Pending requests (need action)
        if pending:
            st.markdown("### 🚨 Needs Your Action")
            for reservation in pending:
                display_owner_reservation_card(reservation)

        # Active reservations
        if active:
            st.markdown("### 🔄 Active Rentals")
            for reservation in active:
                display_owner_reservation_card(reservation)

        # Completed reservations
        if completed:
            st.markdown("### ✅ Completed")
            for reservation in completed:
                display_owner_reservation_card(reservation)

        # Other reservations
        if other:
            st.markdown("### 📜 Past Decisions")
            for reservation in other:
                display_owner_reservation_card(reservation)

    except Exception as e:
        st.error(f"Error loading incoming requests: {str(e)}")


def display_borrower_reservation_card(reservation):
    """Display reservation card from borrower's perspective."""
    with st.container():
        # Status styling
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
        <div style="padding: 1rem; border-left: 4px solid {status_color}; background-color: #f8f9fa; margin-bottom: 1rem; border-radius: 5px;">
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            # Tool and owner info
            tool_name = reservation.tool.title if reservation.tool else "Unknown Tool"
            st.markdown(f"**🔧 {tool_name}**")

            if reservation.tool and reservation.tool.owner:
                owner_name = reservation.tool.owner.full_name or reservation.tool.owner.email
                st.write(f"**Owner:** {owner_name}")

            st.write(f"**Dates:** {reservation.start_date} to {reservation.end_date}")

            # Duration
            duration = (reservation.end_date - reservation.start_date).days + 1
            st.write(f"**Duration:** {duration} day(s)")

            # Status with emoji
            status_emojis = {
                "requested": "🕐",
                "accepted": "✅",
                "declined": "❌",
                "cancelled": "🚫",
                "completed": "🏁",
            }

            emoji = status_emojis.get(reservation.status.value, "")
            st.write(f"**Status:** {emoji} {reservation.status.value.title()}")

        with col2:
            # Action buttons
            if reservation.status == ReservationStatus.REQUESTED:
                if st.button("🚫 Cancel Request", key=f"cancel_{reservation.id}"):
                    update_reservation_status(reservation.id, ReservationStatus.CANCELLED)

            elif reservation.status == ReservationStatus.COMPLETED:
                # Check if review exists
                try:
                    existing_reviews = ReviewService.get_reviews_for_tool(reservation.tool_id)
                    has_reviewed = any(r.reservation_id == reservation.id for r in existing_reviews)

                    if not has_reviewed:
                        if st.button("⭐ Leave Review", key=f"review_{reservation.id}"):
                            st.session_state.review_reservation_id = reservation.id
                            st.session_state.show_review_form = True
                            st.rerun()
                    else:
                        st.info("✅ Reviewed")
                except:
                    pass  # If we can't check reviews, don't show the button

        st.markdown("</div>", unsafe_allow_html=True)


def display_owner_reservation_card(reservation):
    """Display reservation card from owner's perspective."""
    with st.container():
        # Status styling
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
        <div style="padding: 1rem; border-left: 4px solid {status_color}; background-color: #f8f9fa; margin-bottom: 1rem; border-radius: 5px;">
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            # Borrower and tool info
            if reservation.borrower:
                borrower_name = reservation.borrower.full_name or reservation.borrower.email
                st.markdown(f"**👤 {borrower_name}**")

            tool_name = reservation.tool.title if reservation.tool else "Unknown Tool"
            st.write(f"**Tool:** {tool_name}")

            st.write(f"**Dates:** {reservation.start_date} to {reservation.end_date}")

            # Duration
            duration = (reservation.end_date - reservation.start_date).days + 1
            st.write(f"**Duration:** {duration} day(s)")

            # Status
            status_emojis = {
                "requested": "🕐",
                "accepted": "✅",
                "declined": "❌",
                "cancelled": "🚫",
                "completed": "🏁",
            }

            emoji = status_emojis.get(reservation.status.value, "")
            st.write(f"**Status:** {emoji} {reservation.status.value.title()}")

        with col2:
            # Action buttons for owner
            if reservation.status == ReservationStatus.REQUESTED:
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

        if status == ReservationStatus.ACCEPTED:
            st.success("✅ Reservation accepted!")
        elif status == ReservationStatus.DECLINED:
            st.success("❌ Reservation declined!")
        elif status == ReservationStatus.CANCELLED:
            st.success("🚫 Reservation cancelled!")

        st.rerun()
    except Exception as e:
        st.error(f"Failed to update reservation: {str(e)}")


# Handle review form modal
if st.session_state.get("show_review_form", False):
    show_review_form()


def show_review_form():
    """Show review form in a modal-like expander."""
    reservation_id = st.session_state.get("review_reservation_id")
    current_user = get_current_user()

    if reservation_id and current_user:
        with st.expander("⭐ Leave a Review", expanded=True):
            # Close button
            if st.button("❌ Close", key="close_review"):
                st.session_state.show_review_form = False
                st.rerun()

            st.write("How was your experience with this tool?")

            with st.form("review_form"):
                rating = st.selectbox("Rating", [5, 4, 3, 2, 1], format_func=lambda x: "⭐" * x)

                comment = st.text_area(
                    "Review (Optional)",
                    placeholder="Share your experience with this tool and its owner...",
                    max_chars=500,
                )

                submitted = st.form_submit_button("Submit Review", type="primary")

                if submitted:
                    try:
                        ReviewService.create_review(
                            reservation_id=reservation_id,
                            reviewer_id=current_user.id,
                            rating=rating,
                            comment=comment,
                        )

                        st.success("✅ Review submitted successfully!")
                        st.balloons()

                        # Clear the form
                        st.session_state.show_review_form = False
                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to submit review: {str(e)}")


if __name__ == "__main__":
    main()
