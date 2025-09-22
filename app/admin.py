"""Admin panel for ToolShare."""

import streamlit as st

from lib.services import ToolService
from lib.supabase_client import get_current_user, require_auth


def main():
    require_auth()
    current_user = get_current_user()

    # Basic admin check (in a real app, you'd have proper role-based access)
    if not is_admin(current_user):
        st.error("🚫 Access denied. Admin privileges required.")
        st.info(
            "This is a demo admin panel. In a real application, proper role-based access control would be implemented."
        )
        return

    st.title("🛡️ Admin Panel")

    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Users", "🔧 Tools", "📋 Reservations"])

    with tab1:
        show_overview()

    with tab2:
        show_user_management()

    with tab3:
        show_tool_management()

    with tab4:
        show_reservation_management()


def is_admin(user):
    """Check if user has admin privileges."""
    # For demo purposes, any user can access admin panel
    # In a real app, you'd check user roles/permissions
    return True


def show_overview():
    """Show admin overview dashboard."""
    st.subheader("📊 Platform Overview")

    try:
        # Get basic statistics
        all_tools = ToolService.get_tools()
        # For users, we'll show a placeholder since we can't easily count all users
        # In a real app, you'd have proper admin queries

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🔧 Total Tools", len(all_tools))

        with col2:
            active_tools = len([t for t in all_tools if t.is_active])
            st.metric("✅ Active Tools", active_tools)

        with col3:
            # Placeholder for user count
            st.metric("👥 Total Users", "10+")

        with col4:
            # Placeholder for reservation count
            st.metric("📋 Total Reservations", "25+")

        # Recent activity
        st.markdown("### 📈 Recent Activity")

        # Show recent tools
        recent_tools = sorted(all_tools, key=lambda x: x.created_at or "", reverse=True)[:5]

        if recent_tools:
            st.markdown("**Recently Added Tools:**")
            for tool in recent_tools:
                owner_name = (
                    tool.owner.full_name if tool.owner and tool.owner.full_name else "Anonymous"
                )
                st.write(f"• {tool.title} by {owner_name}")

        # Platform health
        st.markdown("### 🏥 Platform Health")

        col1, col2 = st.columns(2)

        with col1:
            st.success("✅ Database: Healthy")
            st.success("✅ Authentication: Operational")

        with col2:
            st.success("✅ Storage: Operational")
            st.success("✅ API: Responsive")

    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")


def show_user_management():
    """Show user management interface."""
    st.subheader("👥 User Management")

    st.info(
        "👨‍💻 **Demo Mode**: In a production environment, this would show all users with proper admin permissions."
    )

    # Search and filters
    col1, col2 = st.columns(2)

    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Search by email or name...")

    with col2:
        user_filter = st.selectbox(
            "Filter by", ["All Users", "Active", "Inactive", "New This Week"]
        )

    # Sample user data for demo
    sample_users = [
        {
            "email": "alice@example.com",
            "name": "Alice Johnson",
            "status": "Active",
            "tools": 3,
            "joined": "2024-01-15",
        },
        {
            "email": "bob@example.com",
            "name": "Bob Smith",
            "status": "Active",
            "tools": 1,
            "joined": "2024-02-01",
        },
        {
            "email": "carol@example.com",
            "name": "Carol Davis",
            "status": "Active",
            "tools": 5,
            "joined": "2024-01-20",
        },
    ]

    # Display users
    st.markdown("### User List")

    for user in sample_users:
        with st.expander(f"👤 {user['name']} ({user['email']})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Status:** {user['status']}")
                st.write(f"**Tools Shared:** {user['tools']}")

            with col2:
                st.write(f"**Joined:** {user['joined']}")
                st.write("**Role:** User")

            with col3:
                if st.button("🔍 View Details", key=f"view_user_{user['email']}"):
                    st.info("User detail view would open here")

                if st.button("✉️ Contact", key=f"contact_{user['email']}"):
                    st.info("Contact user feature would open here")


def show_tool_management():
    """Show tool management interface."""
    st.subheader("🔧 Tool Management")

    try:
        all_tools = ToolService.get_tools()

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            search_term = st.text_input("🔍 Search tools", placeholder="Search by title...")

        with col2:
            category_filter = st.selectbox(
                "Category", ["All Categories"] + list(set([t.category for t in all_tools]))
            )

        with col3:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

        # Apply filters
        filtered_tools = all_tools

        if search_term:
            filtered_tools = [t for t in filtered_tools if search_term.lower() in t.title.lower()]

        if category_filter != "All Categories":
            filtered_tools = [t for t in filtered_tools if t.category == category_filter]

        if status_filter == "Active":
            filtered_tools = [t for t in filtered_tools if t.is_active]
        elif status_filter == "Inactive":
            filtered_tools = [t for t in filtered_tools if not t.is_active]

        st.markdown(f"### Tools ({len(filtered_tools)} found)")

        # Display tools
        for tool in filtered_tools:
            with st.expander(f"🔧 {tool.title} - {tool.category}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(
                        f"**Owner:** {tool.owner.full_name if tool.owner and tool.owner.full_name else 'Anonymous'}"
                    )
                    st.write(f"**Category:** {tool.category}")
                    st.write(f"**Condition:** {tool.condition.value.title()}")

                with col2:
                    st.write(f"**Status:** {'🟢 Active' if tool.is_active else '🔴 Inactive'}")
                    st.write(
                        f"**Price:** ${tool.daily_price:.2f}/day"
                        if tool.daily_price > 0
                        else "Free"
                    )
                    st.write(
                        f"**Created:** {tool.created_at.strftime('%Y-%m-%d') if tool.created_at else 'Unknown'}"
                    )

                with col3:
                    if st.button("🔍 View Details", key=f"admin_view_{tool.id}"):
                        st.info("Tool detail view would open here")

                    action_text = "🔴 Deactivate" if tool.is_active else "🟢 Activate"
                    if st.button(action_text, key=f"admin_toggle_{tool.id}"):
                        st.info("Tool status toggle would happen here")

                    if st.button("🗑️ Remove", key=f"admin_remove_{tool.id}"):
                        st.warning("Tool removal would happen here (with confirmation)")

    except Exception as e:
        st.error(f"Error loading tools: {str(e)}")


def show_reservation_management():
    """Show reservation management interface."""
    st.subheader("📋 Reservation Management")

    st.info(
        "👨‍💻 **Demo Mode**: In a production environment, this would show all reservations with admin controls."
    )

    # Sample reservation data
    sample_reservations = [
        {
            "id": "res1",
            "tool": "Power Drill",
            "borrower": "alice@example.com",
            "owner": "bob@example.com",
            "status": "Accepted",
            "dates": "2024-03-15 to 2024-03-17",
            "created": "2024-03-10",
        },
        {
            "id": "res2",
            "tool": "Lawn Mower",
            "borrower": "carol@example.com",
            "owner": "alice@example.com",
            "status": "Requested",
            "dates": "2024-03-20 to 2024-03-22",
            "created": "2024-03-12",
        },
        {
            "id": "res3",
            "tool": "Projector",
            "borrower": "bob@example.com",
            "owner": "carol@example.com",
            "status": "Completed",
            "dates": "2024-03-01 to 2024-03-03",
            "created": "2024-02-25",
        },
    ]

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Requested", "Accepted", "Completed", "Declined", "Cancelled"],
        )

    with col2:
        date_filter = st.selectbox(
            "Date Range", ["All Time", "This Week", "This Month", "Last Month"]
        )

    # Display reservations
    st.markdown("### Reservation List")

    for reservation in sample_reservations:
        # Status color coding
        status_colors = {
            "Requested": "#ffa500",
            "Accepted": "#28a745",
            "Completed": "#17a2b8",
            "Declined": "#dc3545",
            "Cancelled": "#6c757d",
        }

        status_color = status_colors.get(reservation["status"], "#6c757d")

        with st.container():
            st.markdown(
                f"""
            <div style="padding: 1rem; border-left: 4px solid {status_color}; background-color: #f8f9fa; margin-bottom: 1rem;">
            """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(f"**Tool:** {reservation['tool']}")
                st.write(f"**Borrower:** {reservation['borrower']}")
                st.write(f"**Owner:** {reservation['owner']}")

            with col2:
                st.write(f"**Status:** {reservation['status']}")
                st.write(f"**Dates:** {reservation['dates']}")
                st.write(f"**Created:** {reservation['created']}")

            with col3:
                if st.button("🔍 Details", key=f"admin_res_view_{reservation['id']}"):
                    st.info("Reservation details would open here")

                if reservation["status"] in ["Requested", "Accepted"]:
                    if st.button("❌ Cancel", key=f"admin_res_cancel_{reservation['id']}"):
                        st.warning("Admin cancellation would happen here")

            st.markdown("</div>", unsafe_allow_html=True)

    # Admin actions
    st.markdown("---")
    st.markdown("### 🛠️ Admin Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Generate Report"):
            st.info("Report generation would happen here")

    with col2:
        if st.button("📧 Send Notifications"):
            st.info("Bulk notification sending would happen here")

    with col3:
        if st.button("🧹 Cleanup Old Data"):
            st.info("Data cleanup would happen here")


if __name__ == "__main__":
    main()
