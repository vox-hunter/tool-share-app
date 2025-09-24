"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Admin panel for ToolShare application.
"""
import streamlit as st
from lib.auth import require_login, get_current_user, is_admin
from lib.services import ToolService, ReservationService, ReviewService
from lib.db import get_connection
import json

def require_admin():
    """Require admin access."""
    require_login()
    current_user = get_current_user()
    if not current_user or not is_admin(current_user['id']):
        st.error("Access denied. Admin privileges required.")
        st.stop()

def get_all_users():
    """Get all users from database."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, full_name, created_at FROM users ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_reservations():
    """Get all reservations with details."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT r.*, t.title as tool_title, t.owner_id,
                   b.username as borrower_username, b.full_name as borrower_name,
                   o.username as owner_username, o.full_name as owner_name
            FROM reservations r
            JOIN tools t ON r.tool_id = t.id
            JOIN users b ON r.borrower_id = b.id
            JOIN users o ON t.owner_id = o.id
            ORDER BY r.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_reviews():
    """Get all reviews with details."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT rv.*, r.tool_id, t.title as tool_title,
                   u.username as reviewer_username, u.full_name as reviewer_name,
                   o.username as owner_username, o.full_name as owner_name
            FROM reviews rv
            JOIN reservations r ON rv.reservation_id = r.id
            JOIN tools t ON r.tool_id = t.id
            JOIN users u ON rv.reviewer_id = u.id
            JOIN users o ON t.owner_id = o.id
            ORDER BY rv.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_audit_logs():
    """Get recent audit logs."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT al.*, u.username, u.full_name
            FROM audit_logs al
            LEFT JOIN users u ON al.actor_id = u.id
            ORDER BY al.created_at DESC
            LIMIT 100
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def render_users_tab():
    """Render users management tab."""
    st.subheader("👥 Users")
    
    users = get_all_users()
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        recent_users = len([u for u in users if u['created_at'] >= '2024-01-01'])
        st.metric("Recent Signups", recent_users)
    with col3:
        admin_count = len([u for u in users if is_admin(u['id'])])
        st.metric("Admins", admin_count)
    
    st.markdown("---")
    
    # Users table
    if users:
        st.dataframe(
            users,
            column_config={
                "id": "ID",
                "username": "Username",
                "full_name": "Full Name",
                "created_at": "Joined",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No users found")

def render_tools_tab():
    """Render tools management tab."""
    st.subheader("🔧 Tools")
    
    tools = ToolService.get_tools(active_only=False)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tools", len(tools))
    with col2:
        active_tools = len([t for t in tools if t['is_active']])
        st.metric("Active", active_tools)
    with col3:
        inactive_tools = len(tools) - active_tools
        st.metric("Inactive", inactive_tools)
    with col4:
        categories = len(set(t['category'] for t in tools))
        st.metric("Categories", categories)
    
    st.markdown("---")
    
    # Tools table
    if tools:
        # Convert for display
        tools_display = []
        for tool in tools:
            tools_display.append({
                "id": tool['id'],
                "title": tool['title'],
                "category": tool['category'],
                "condition": tool['condition'],
                "owner": tool['full_name'],
                "active": "✅" if tool['is_active'] else "❌",
                "created_at": tool['created_at'][:10]
            })
        
        st.dataframe(
            tools_display,
            column_config={
                "id": "ID",
                "title": "Title",
                "category": "Category",
                "condition": "Condition",
                "owner": "Owner",
                "active": "Status",
                "created_at": "Created",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No tools found")

def render_reservations_tab():
    """Render reservations management tab."""
    st.subheader("📅 Reservations")
    
    reservations = get_all_reservations()
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reservations", len(reservations))
    with col2:
        requested = len([r for r in reservations if r['status'] == 'requested'])
        st.metric("Pending", requested)
    with col3:
        accepted = len([r for r in reservations if r['status'] == 'accepted'])
        st.metric("Active", accepted)
    with col4:
        completed = len([r for r in reservations if r['status'] == 'completed'])
        st.metric("Completed", completed)
    
    st.markdown("---")
    
    # Reservations table
    if reservations:
        # Convert for display
        reservations_display = []
        for res in reservations:
            status_emoji = {
                'requested': '⏳',
                'accepted': '✅',
                'declined': '❌',
                'cancelled': '🚫',
                'completed': '✅'
            }
            
            reservations_display.append({
                "id": res['id'],
                "tool": res['tool_title'],
                "borrower": res['borrower_name'],
                "owner": res['owner_name'],
                "start_date": res['start_date'],
                "end_date": res['end_date'],
                "status": f"{status_emoji.get(res['status'], '❓')} {res['status'].title()}",
                "created_at": res['created_at'][:10]
            })
        
        st.dataframe(
            reservations_display,
            column_config={
                "id": "ID",
                "tool": "Tool",
                "borrower": "Borrower",
                "owner": "Owner",
                "start_date": "Start",
                "end_date": "End",
                "status": "Status",
                "created_at": "Created",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No reservations found")

def render_reviews_tab():
    """Render reviews management tab."""
    st.subheader("⭐ Reviews")
    
    reviews = get_all_reviews()
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", len(reviews))
    with col2:
        if reviews:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        else:
            st.metric("Average Rating", "N/A")
    with col3:
        recent_reviews = len([r for r in reviews if r['created_at'] >= '2024-01-01'])
        st.metric("Recent Reviews", recent_reviews)
    
    st.markdown("---")
    
    # Reviews table
    if reviews:
        # Convert for display
        reviews_display = []
        for review in reviews:
            stars = "⭐" * review['rating']
            
            reviews_display.append({
                "id": review['id'],
                "tool": review['tool_title'],
                "rating": f"{stars} ({review['rating']}/5)",
                "reviewer": review['reviewer_name'],
                "owner": review['owner_name'],
                "comment": review['comment'][:50] + "..." if review['comment'] and len(review['comment']) > 50 else review['comment'] or "",
                "created_at": review['created_at'][:10]
            })
        
        st.dataframe(
            reviews_display,
            column_config={
                "id": "ID",
                "tool": "Tool",
                "rating": "Rating",
                "reviewer": "Reviewer",
                "owner": "Tool Owner",
                "comment": "Comment",
                "created_at": "Created",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No reviews found")

def render_logs_tab():
    """Render audit logs tab."""
    st.subheader("📜 Audit Logs")
    
    logs = get_audit_logs()
    
    if logs:
        # Convert for display
        logs_display = []
        for log in logs:
            actor_name = log['full_name'] if log['full_name'] else "System"
            
            # Parse JSON payload for display
            payload_text = ""
            if log['json_payload']:
                try:
                    payload = json.loads(log['json_payload'])
                    payload_text = str(payload)[:100] + "..." if len(str(payload)) > 100 else str(payload)
                except (json.JSONDecodeError, TypeError):
                    payload_text = log['json_payload'][:100]
            
            logs_display.append({
                "id": log['id'],
                "actor": actor_name,
                "action": log['action_type'],
                "details": payload_text,
                "timestamp": log['created_at'][:19]
            })
        
        st.dataframe(
            logs_display,
            column_config={
                "id": "ID",
                "actor": "Actor",
                "action": "Action",
                "details": "Details",
                "timestamp": "Timestamp",
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No audit logs found")

def render_system_stats():
    """Render system statistics."""
    st.subheader("📊 System Overview")
    
    # Get all data for stats
    users = get_all_users()
    tools = ToolService.get_tools(active_only=False)
    reservations = get_all_reservations()
    reviews = get_all_reviews()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", len(users))
    
    with col2:
        st.metric("Total Tools", len(tools))
    
    with col3:
        st.metric("Total Reservations", len(reservations))
    
    with col4:
        st.metric("Total Reviews", len(reviews))
    
    st.markdown("---")
    
    # Secondary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_tools = len([t for t in tools if t['is_active']])
        st.metric("Active Tools", active_tools)
    
    with col2:
        completed_reservations = len([r for r in reservations if r['status'] == 'completed'])
        st.metric("Completed Reservations", completed_reservations)
    
    with col3:
        if reviews:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        else:
            st.metric("Average Rating", "N/A")
    
    with col4:
        categories = len(set(t['category'] for t in tools))
        st.metric("Tool Categories", categories)

def main():
    """Main admin page function."""
    st.set_page_config(
        page_title="ToolShare - Admin Panel",
        page_icon="🛡️",
        layout="wide"
    )
    
    # Require admin access
    require_admin()
    
    st.title("🛡️ Admin Panel")
    st.write("System administration and monitoring")
    
    # System overview
    render_system_stats()
    
    st.markdown("---")
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Users", "🔧 Tools", "📅 Reservations", "⭐ Reviews", "📜 Logs"])
    
    with tab1:
        render_users_tab()
    
    with tab2:
        render_tools_tab()
    
    with tab3:
        render_reservations_tab()
    
    with tab4:
        render_reviews_tab()
    
    with tab5:
        render_logs_tab()
    
    # Back to main app
    st.markdown("---")
    if st.button("← Back to Main App", use_container_width=True):
        st.switch_page("home.py")

if __name__ == "__main__":
    main()