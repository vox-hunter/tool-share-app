"""
Local authentication system for ToolShare.
"""
import bcrypt
import streamlit as st
import sqlite3
from typing import Optional, Dict
from lib.db import get_connection, log_action
import logging

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username: str, password: str, full_name: str, bio: str = "") -> Optional[int]:
    """
    Create a new user account.
    Returns user ID if successful, None if username already exists.
    """
    conn = get_connection()
    try:
        # Check if username already exists
        cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return None
            
        # Create new user
        password_hash = hash_password(password)
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, full_name, bio) VALUES (?, ?, ?, ?)",
            (username, password_hash, full_name, bio)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        log_action(user_id, "user_created", {"username": username, "full_name": full_name})
        logger.info(f"User created: {username} (ID: {user_id})")
        return user_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating user: {e}")
        return None
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with username and password.
    Returns user data if successful, None otherwise.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, password_hash, full_name, avatar_path, bio, created_at FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            user_data = dict(user)
            del user_data['password_hash']  # Remove password hash from returned data
            log_action(user['id'], "user_login", {"username": username})
            return user_data
        return None
        
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user data by ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, full_name, avatar_path, bio, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        return dict(user) if user else None
        
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
    finally:
        conn.close()

def update_user_profile(user_id: int, full_name: str, bio: str, avatar_path: Optional[str] = None) -> bool:
    """Update user profile information."""
    conn = get_connection()
    try:
        if avatar_path:
            conn.execute(
                "UPDATE users SET full_name = ?, bio = ?, avatar_path = ? WHERE id = ?",
                (full_name, bio, avatar_path, user_id)
            )
        else:
            conn.execute(
                "UPDATE users SET full_name = ?, bio = ? WHERE id = ?",
                (full_name, bio, user_id)
            )
        conn.commit()
        
        log_action(user_id, "profile_updated", {"full_name": full_name, "bio": bio})
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating profile: {e}")
        return False
    finally:
        conn.close()

def is_logged_in() -> bool:
    """Check if user is currently logged in."""
    return 'user_id' in st.session_state and st.session_state.user_id is not None

def get_current_user() -> Optional[Dict]:
    """Get current logged-in user data."""
    if not is_logged_in():
        return None
    return get_user_by_id(st.session_state.user_id)

def logout():
    """Log out the current user."""
    if is_logged_in():
        log_action(st.session_state.user_id, "user_logout", {})
    
    # Clear session state
    for key in ['user_id', 'username', 'user_data']:
        if key in st.session_state:
            del st.session_state[key]

def require_login():
    """Decorator/helper to require login for a page."""
    if not is_logged_in():
        st.error("Please log in to access this page.")
        st.stop()

def is_admin(user_id: Optional[int] = None) -> bool:
    """Check if user has admin privileges (user ID 1 for simplicity)."""
    if user_id is None:
        user_id = st.session_state.get('user_id')
    return user_id == 1