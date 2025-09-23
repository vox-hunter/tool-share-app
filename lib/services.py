"""
Core business logic services for ToolShare.
"""
import json
import sqlite3
from typing import List, Dict, Optional
from datetime import date
from lib.db import get_connection, check_reservation_conflict, log_action
from lib.storage import delete_images
import logging

logger = logging.getLogger(__name__)

class ToolService:
    """Service for managing tools."""
    
    @staticmethod
    def create_tool(owner_id: int, title: str, description: str, category: str, 
                   condition: str, price: float, contact_info: str, image_paths: List[str]) -> Optional[int]:
        """Create a new tool."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO tools (owner_id, title, description, category, condition, price, contact_info, image_paths)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (owner_id, title, description, category, condition, price, contact_info, json.dumps(image_paths))
            )
            tool_id = cursor.lastrowid
            conn.commit()
            
            log_action(owner_id, "tool_created", {
                "tool_id": tool_id, "title": title, "category": category
            })
            logger.info("Tool created: %s (ID: %s) by user %s", title, tool_id, owner_id)
            return tool_id
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error("Error creating tool: %s", e)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_tool(tool_id: int) -> Optional[Dict]:
        """Get tool by ID with owner information."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT t.*, u.username, u.full_name, u.avatar_path 
                   FROM tools t 
                   JOIN users u ON t.owner_id = u.id 
                   WHERE t.id = ?""",
                (tool_id,)
            )
            tool = cursor.fetchone()
            if tool:
                tool_data = dict(tool)
                # Parse image paths from JSON
                tool_data['image_paths'] = json.loads(tool_data['image_paths'] or '[]')
                return tool_data
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching tool: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_tools(category: Optional[str] = None, search: Optional[str] = None, 
                 owner_id: Optional[int] = None, active_only: bool = True) -> List[Dict]:
        """Get tools with optional filtering."""
        conn = get_connection()
        try:
            query = """
                SELECT t.*, u.username, u.full_name, u.avatar_path 
                FROM tools t 
                JOIN users u ON t.owner_id = u.id 
                WHERE 1=1
            """
            params = []
            
            if active_only:
                query += " AND t.is_active = 1"
            
            if category:
                query += " AND t.category = ?"
                params.append(category)
            
            if search:
                query += " AND (t.title LIKE ? OR t.description LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            
            if owner_id:
                query += " AND t.owner_id = ?"
                params.append(owner_id)
            
            query += " ORDER BY t.created_at DESC"
            
            cursor = conn.execute(query, params)
            tools = []
            for row in cursor.fetchall():
                tool_data = dict(row)
                tool_data['image_paths'] = json.loads(tool_data['image_paths'] or '[]')
                tools.append(tool_data)
            
            return tools
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching tools: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_tool(tool_id: int, user_id: int, title: str, description: str, 
                   category: str, condition: str, price: float, contact_info: str, image_paths: List[str]) -> bool:
        """Update tool (only by owner)."""
        conn = get_connection()
        try:
            # Check ownership
            cursor = conn.execute("SELECT owner_id FROM tools WHERE id = ?", (tool_id,))
            tool = cursor.fetchone()
            if not tool or tool['owner_id'] != user_id:
                return False
            
            conn.execute(
                """UPDATE tools 
                   SET title = ?, description = ?, category = ?, condition = ?, 
                       price = ?, contact_info = ?, image_paths = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (title, description, category, condition, price, contact_info, json.dumps(image_paths), tool_id)
            )
            conn.commit()
            
            log_action(user_id, "tool_updated", {"tool_id": tool_id, "title": title})
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error updating tool: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete_tool(tool_id: int, user_id: int) -> bool:
        """Delete tool (only by owner, soft delete if has reservations)."""
        conn = get_connection()
        try:
            # Check ownership
            cursor = conn.execute("SELECT owner_id, image_paths FROM tools WHERE id = ?", (tool_id,))
            tool = cursor.fetchone()
            if not tool or tool['owner_id'] != user_id:
                return False
            
            # Always use soft delete to avoid foreign key constraints
            # Tools with any reservations (past or present) should not be hard deleted
            cursor = conn.execute(
                "SELECT COUNT(*) FROM reservations WHERE tool_id = ?",
                (tool_id,)
            )
            any_reservations = cursor.fetchone()[0]
            
            if any_reservations > 0:
                # Soft delete - mark as inactive (has reservation history)
                conn.execute("UPDATE tools SET is_active = 0 WHERE id = ?", (tool_id,))
                log_action(user_id, "tool_deactivated", {"tool_id": tool_id})
            else:
                # Soft delete for consistency (can be changed to hard delete if needed)
                conn.execute("UPDATE tools SET is_active = 0 WHERE id = ?", (tool_id,))
                log_action(user_id, "tool_deactivated", {"tool_id": tool_id})
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error deleting tool: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get all unique tool categories."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT DISTINCT category FROM tools WHERE is_active = 1 ORDER BY category"
            )
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching categories: {e}")
            return []
        finally:
            conn.close()


class ReservationService:
    """Service for managing reservations."""
    
    @staticmethod
    def create_reservation(tool_id: int, borrower_id: int, start_date: str, end_date: str) -> Optional[int]:
        """Create a new reservation request."""
        conn = get_connection()
        try:
            # Check for conflicts
            if check_reservation_conflict(tool_id, start_date, end_date):
                return None
            
            # Check tool exists and is active
            cursor = conn.execute(
                "SELECT owner_id FROM tools WHERE id = ? AND is_active = 1", 
                (tool_id,)
            )
            tool = cursor.fetchone()
            if not tool:
                return None
            
            # Don't allow owner to reserve their own tool
            if tool['owner_id'] == borrower_id:
                return None
            
            cursor = conn.execute(
                """INSERT INTO reservations (tool_id, borrower_id, start_date, end_date)
                   VALUES (?, ?, ?, ?)""",
                (tool_id, borrower_id, start_date, end_date)
            )
            reservation_id = cursor.lastrowid
            conn.commit()
            
            log_action(borrower_id, "reservation_requested", {
                "reservation_id": reservation_id, "tool_id": tool_id
            })
            logger.info(f"Reservation created: {reservation_id} for tool {tool_id}")
            return reservation_id
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error creating reservation: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_reservation(reservation_id: int) -> Optional[Dict]:
        """Get reservation with tool and user information."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT r.*, t.title as tool_title, t.owner_id,
                          b.username as borrower_username, b.full_name as borrower_name,
                          o.username as owner_username, o.full_name as owner_name
                   FROM reservations r
                   JOIN tools t ON r.tool_id = t.id
                   JOIN users b ON r.borrower_id = b.id
                   JOIN users o ON t.owner_id = o.id
                   WHERE r.id = ?""",
                (reservation_id,)
            )
            reservation = cursor.fetchone()
            return dict(reservation) if reservation else None
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching reservation: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_reservations(user_id: int, as_borrower: bool = True) -> List[Dict]:
        """Get reservations for a user (as borrower or owner)."""
        conn = get_connection()
        try:
            if as_borrower:
                query = """
                    SELECT r.*, t.title as tool_title, t.owner_id,
                           o.username as owner_username, o.full_name as owner_name
                    FROM reservations r
                    JOIN tools t ON r.tool_id = t.id
                    JOIN users o ON t.owner_id = o.id
                    WHERE r.borrower_id = ?
                    ORDER BY r.created_at DESC
                """
                params = (user_id,)
            else:
                query = """
                    SELECT r.*, t.title as tool_title,
                           b.username as borrower_username, b.full_name as borrower_name
                    FROM reservations r
                    JOIN tools t ON r.tool_id = t.id
                    JOIN users b ON r.borrower_id = b.id
                    WHERE t.owner_id = ?
                    ORDER BY r.created_at DESC
                """
                params = (user_id,)
            
            cursor = conn.execute(query, params)
            reservations = []
            for row in cursor.fetchall():
                reservations.append(dict(row))
            
            return reservations
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching user reservations: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_reservation_status(reservation_id: int, user_id: int, status: str) -> bool:
        """Update reservation status (approve/decline by owner, cancel by borrower)."""
        conn = get_connection()
        try:
            # Get reservation details
            reservation = ReservationService.get_reservation(reservation_id)
            if not reservation:
                return False
            
            # Check permissions
            if status in ['accepted', 'declined'] and reservation['owner_id'] != user_id:
                return False  # Only owner can approve/decline
            elif status == 'cancelled' and reservation['borrower_id'] != user_id:
                return False  # Only borrower can cancel
            
            # Check for conflicts when accepting
            if status == 'accepted':
                if check_reservation_conflict(
                    reservation['tool_id'], 
                    reservation['start_date'], 
                    reservation['end_date'],
                    reservation_id
                ):
                    return False
            
            conn.execute(
                "UPDATE reservations SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, reservation_id)
            )
            conn.commit()
            
            log_action(user_id, f"reservation_{status}", {"reservation_id": reservation_id})
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error updating reservation status: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def mark_completed(reservation_id: int) -> bool:
        """Mark reservation as completed (automatic based on end date)."""
        conn = get_connection()
        try:
            conn.execute(
                """UPDATE reservations 
                   SET status = 'completed', updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ? AND status = 'accepted' AND end_date < date('now')""",
                (reservation_id,)
            )
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error marking reservation completed: {e}")
            return False
        finally:
            conn.close()


class ReviewService:
    """Service for managing reviews."""
    
    @staticmethod
    def can_review(reservation_id: int, user_id: int) -> bool:
        """Check if user can review this reservation."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT r.borrower_id, r.status, r.end_date, t.owner_id,
                          rv.id as existing_review_id
                   FROM reservations r
                   JOIN tools t ON r.tool_id = t.id
                   LEFT JOIN reviews rv ON rv.reservation_id = r.id
                   WHERE r.id = ?""",
                (reservation_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                return False
                
            # Must be completed reservation
            if result['status'] != 'completed':
                return False
                
            # Must be past end date
            if result['end_date'] >= date.today().isoformat():
                return False
                
            # User must be either borrower or owner
            if user_id not in [result['borrower_id'], result['owner_id']]:
                return False
                
            # No existing review
            if result['existing_review_id']:
                return False
                
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error checking review eligibility: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def create_review(reservation_id: int, reviewer_id: int, rating: int, comment: str) -> Optional[int]:
        """Create a review for a completed reservation."""
        if not ReviewService.can_review(reservation_id, reviewer_id):
            return None
            
        conn = get_connection()
        try:
            cursor = conn.execute(
                """INSERT INTO reviews (reservation_id, reviewer_id, rating, comment)
                   VALUES (?, ?, ?, ?)""",
                (reservation_id, reviewer_id, rating, comment)
            )
            review_id = cursor.lastrowid
            conn.commit()
            
            log_action(reviewer_id, "review_created", {
                "review_id": review_id, "reservation_id": reservation_id, "rating": rating
            })
            return review_id
            
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Error creating review: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_reviews(user_id: int) -> List[Dict]:
        """Get reviews about a user (as tool owner)."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT rv.*, r.tool_id, t.title as tool_title,
                          u.username as reviewer_username, u.full_name as reviewer_name
                   FROM reviews rv
                   JOIN reservations r ON rv.reservation_id = r.id
                   JOIN tools t ON r.tool_id = t.id
                   JOIN users u ON rv.reviewer_id = u.id
                   WHERE t.owner_id = ?
                   ORDER BY rv.created_at DESC""",
                (user_id,)
            )
            reviews = []
            for row in cursor.fetchall():
                reviews.append(dict(row))
            return reviews
            
        except sqlite3.Error as e:
            logger.error(f"Error fetching user reviews: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_user_rating(user_id: int) -> float:
        """Get average rating for a user."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                """SELECT AVG(rv.rating)
                   FROM reviews rv
                   JOIN reservations r ON rv.reservation_id = r.id
                   JOIN tools t ON r.tool_id = t.id
                   WHERE t.owner_id = ?""",
                (user_id,)
            )
            result = cursor.fetchone()
            return round(result[0], 1) if result[0] else 0.0
            
        except sqlite3.Error as e:
            logger.error(f"Error calculating user rating: {e}")
            return 0.0
        finally:
            conn.close()
