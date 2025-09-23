"""
Database connection and migration utilities for ToolShare.
"""
import sqlite3
import os
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_PATH = "toolshare.db"

def get_connection() -> sqlite3.Connection:
    """Get a database connection with proper configuration."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

def init_database():
    """Initialize the database with all required tables."""
    conn = get_connection()
    try:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                avatar_path TEXT,
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tools table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                condition TEXT NOT NULL CHECK (condition IN ('new', 'good', 'fair')),
                image_paths TEXT, -- JSON array of image paths
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        """)
        
        # Reservations table with overlap prevention
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                borrower_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status TEXT NOT NULL DEFAULT 'requested' CHECK (
                    status IN ('requested', 'accepted', 'declined', 'cancelled', 'completed')
                ),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tool_id) REFERENCES tools (id),
                FOREIGN KEY (borrower_id) REFERENCES users (id)
            )
        """)
        
        # Reviews table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_id INTEGER NOT NULL UNIQUE,
                reviewer_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservation_id) REFERENCES reservations (id),
                FOREIGN KEY (reviewer_id) REFERENCES users (id)
            )
        """)
        
        # Audit logs table (optional)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                action_type TEXT NOT NULL,
                json_payload TEXT, -- JSON data
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (actor_id) REFERENCES users (id)
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tools_owner ON tools (owner_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tools_category ON tools (category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reservations_tool ON reservations (tool_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reservations_borrower ON reservations (borrower_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations (start_date, end_date)")
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

def check_reservation_conflict(tool_id: int, start_date: str, end_date: str, 
                             exclude_reservation_id: Optional[int] = None) -> bool:
    """
    Check if a reservation conflicts with existing accepted reservations.
    Returns True if there's a conflict, False otherwise.
    """
    conn = get_connection()
    try:
        query = """
            SELECT COUNT(*) FROM reservations 
            WHERE tool_id = ? 
            AND status = 'accepted'
            AND (
                (start_date <= ? AND end_date >= ?) OR
                (start_date <= ? AND end_date >= ?) OR
                (start_date >= ? AND end_date <= ?)
            )
        """
        params = [tool_id, start_date, start_date, end_date, end_date, start_date, end_date]
        
        if exclude_reservation_id:
            query += " AND id != ?"
            params.append(exclude_reservation_id)
            
        cursor = conn.execute(query, params)
        count = cursor.fetchone()[0]
        return count > 0
        
    finally:
        conn.close()

def log_action(actor_id: Optional[int], action_type: str, payload: Dict[str, Any]):
    """Log an action to the audit log."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO audit_logs (actor_id, action_type, json_payload) VALUES (?, ?, ?)",
            (actor_id, action_type, json.dumps(payload))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging action: {e}")
    finally:
        conn.close()

# Initialize database on import
if __name__ == "__main__":
    init_database()