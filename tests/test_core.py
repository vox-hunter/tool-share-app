"""
Unit tests for ToolShare core functionality.
"""
import pytest
import tempfile
import os
import sqlite3
from datetime import date, timedelta

# Add the project root to the path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import init_database, get_connection, check_reservation_conflict
from lib.auth import create_user, authenticate_user, hash_password, verify_password
from lib.services import ToolService, ReservationService, ReviewService

# Test database path
TEST_DB_PATH = "test_toolshare.db"

@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database for each test."""
    # Store original database path
    import lib.db
    original_db_path = lib.db.DATABASE_PATH
    
    # Set test database path
    lib.db.DATABASE_PATH = TEST_DB_PATH
    
    # Initialize test database
    init_database()
    
    yield TEST_DB_PATH
    
    # Cleanup
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Restore original path
    lib.db.DATABASE_PATH = original_db_path

class TestAuth:
    """Test authentication functionality."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_create_user(self, test_db):
        """Test user creation."""
        user_id = create_user("testuser", "password123", "Test User", "Test bio")
        assert user_id is not None
        assert isinstance(user_id, int)
        
        # Test duplicate username
        duplicate_id = create_user("testuser", "password456", "Another User", "Another bio")
        assert duplicate_id is None
    
    def test_authenticate_user(self, test_db):
        """Test user authentication."""
        # Create user
        user_id = create_user("testuser", "password123", "Test User", "Test bio")
        assert user_id is not None
        
        # Test successful authentication
        user_data = authenticate_user("testuser", "password123")
        assert user_data is not None
        assert user_data['id'] == user_id
        assert user_data['username'] == "testuser"
        assert user_data['full_name'] == "Test User"
        assert 'password_hash' not in user_data  # Should be removed
        
        # Test failed authentication
        assert authenticate_user("testuser", "wrong_password") is None
        assert authenticate_user("nonexistent", "password123") is None

class TestToolService:
    """Test tool management functionality."""
    
    def test_create_tool(self, test_db):
        """Test tool creation."""
        # Create user first
        user_id = create_user("testuser", "password123", "Test User", "Test bio")
        
        tool_id = ToolService.create_tool(
            user_id, "Test Drill", "A powerful drill", "Power Tools", "good", []
        )
        assert tool_id is not None
        assert isinstance(tool_id, int)
    
    def test_get_tool(self, test_db):
        """Test tool retrieval."""
        # Create user and tool
        user_id = create_user("testuser", "password123", "Test User", "Test bio")
        tool_id = ToolService.create_tool(
            user_id, "Test Drill", "A powerful drill", "Power Tools", "good", []
        )
        
        tool = ToolService.get_tool(tool_id)
        assert tool is not None
        assert tool['id'] == tool_id
        assert tool['title'] == "Test Drill"
        assert tool['owner_id'] == user_id
        assert tool['username'] == "testuser"
    
    def test_get_tools_filtering(self, test_db):
        """Test tool filtering."""
        # Create users and tools
        user1 = create_user("user1", "password123", "User One", "")
        user2 = create_user("user2", "password123", "User Two", "")
        
        tool1 = ToolService.create_tool(user1, "Drill", "Power drill", "Power Tools", "good", [])
        tool2 = ToolService.create_tool(user1, "Saw", "Circular saw", "Power Tools", "new", [])
        tool3 = ToolService.create_tool(user2, "Mower", "Lawn mower", "Garden Tools", "fair", [])
        
        # Test category filter
        power_tools = ToolService.get_tools(category="Power Tools")
        assert len(power_tools) == 2
        
        garden_tools = ToolService.get_tools(category="Garden Tools")
        assert len(garden_tools) == 1
        
        # Test owner filter
        user1_tools = ToolService.get_tools(owner_id=user1)
        assert len(user1_tools) == 2
        
        # Test search
        drill_tools = ToolService.get_tools(search="drill")
        assert len(drill_tools) == 1
        assert drill_tools[0]['title'] == "Drill"
    
    def test_update_tool(self, test_db):
        """Test tool updates."""
        # Create user and tool
        user_id = create_user("testuser", "password123", "Test User", "Test bio")
        tool_id = ToolService.create_tool(
            user_id, "Test Drill", "A powerful drill", "Power Tools", "good", []
        )
        
        # Update tool
        success = ToolService.update_tool(
            tool_id, user_id, "Updated Drill", "An updated drill", "Hand Tools", "new", []
        )
        assert success
        
        # Verify update
        tool = ToolService.get_tool(tool_id)
        assert tool['title'] == "Updated Drill"
        assert tool['category'] == "Hand Tools"
        assert tool['condition'] == "new"
        
        # Test unauthorized update
        other_user = create_user("otheruser", "password123", "Other User", "")
        unauthorized = ToolService.update_tool(
            tool_id, other_user, "Hacked", "Hacked description", "Other", "fair", []
        )
        assert not unauthorized

class TestReservationService:
    """Test reservation functionality."""
    
    def test_create_reservation(self, test_db):
        """Test reservation creation."""
        # Create users and tool
        owner_id = create_user("owner", "password123", "Tool Owner", "")
        borrower_id = create_user("borrower", "password123", "Tool Borrower", "")
        tool_id = ToolService.create_tool(
            owner_id, "Test Tool", "A test tool", "Power Tools", "good", []
        )
        
        # Create reservation
        today = date.today()
        start_date = (today + timedelta(days=1)).isoformat()
        end_date = (today + timedelta(days=3)).isoformat()
        
        reservation_id = ReservationService.create_reservation(
            tool_id, borrower_id, start_date, end_date
        )
        assert reservation_id is not None
        
        # Test owner can't reserve own tool
        owner_reservation = ReservationService.create_reservation(
            tool_id, owner_id, start_date, end_date
        )
        assert owner_reservation is None
    
    def test_reservation_conflict(self, test_db):
        """Test reservation conflict detection."""
        # Create users and tool
        owner_id = create_user("owner", "password123", "Tool Owner", "")
        borrower1_id = create_user("borrower1", "password123", "Borrower One", "")
        borrower2_id = create_user("borrower2", "password123", "Borrower Two", "")
        tool_id = ToolService.create_tool(
            owner_id, "Test Tool", "A test tool", "Power Tools", "good", []
        )
        
        # Create first reservation
        today = date.today()
        start_date = (today + timedelta(days=1)).isoformat()
        end_date = (today + timedelta(days=3)).isoformat()
        
        reservation1_id = ReservationService.create_reservation(
            tool_id, borrower1_id, start_date, end_date
        )
        assert reservation1_id is not None
        
        # Accept the first reservation
        success = ReservationService.update_reservation_status(
            reservation1_id, owner_id, 'accepted'
        )
        assert success
        
        # Try to create conflicting reservation
        conflicting_start = (today + timedelta(days=2)).isoformat()
        conflicting_end = (today + timedelta(days=4)).isoformat()
        
        reservation2_id = ReservationService.create_reservation(
            tool_id, borrower2_id, conflicting_start, conflicting_end
        )
        assert reservation2_id is None  # Should fail due to conflict
    
    def test_reservation_status_updates(self, test_db):
        """Test reservation status updates."""
        # Create users and tool
        owner_id = create_user("owner", "password123", "Tool Owner", "")
        borrower_id = create_user("borrower", "password123", "Tool Borrower", "")
        tool_id = ToolService.create_tool(
            owner_id, "Test Tool", "A test tool", "Power Tools", "good", []
        )
        
        # Create reservation
        today = date.today()
        start_date = (today + timedelta(days=1)).isoformat()
        end_date = (today + timedelta(days=3)).isoformat()
        
        reservation_id = ReservationService.create_reservation(
            tool_id, borrower_id, start_date, end_date
        )
        
        # Test owner can approve
        success = ReservationService.update_reservation_status(
            reservation_id, owner_id, 'accepted'
        )
        assert success
        
        # Test borrower can cancel
        success = ReservationService.update_reservation_status(
            reservation_id, borrower_id, 'cancelled'
        )
        assert success
        
        # Test unauthorized status change
        other_user = create_user("other", "password123", "Other User", "")
        unauthorized = ReservationService.update_reservation_status(
            reservation_id, other_user, 'accepted'
        )
        assert not unauthorized

class TestReviewService:
    """Test review functionality."""
    
    def test_review_eligibility(self, test_db):
        """Test review eligibility checks."""
        # Create users and tool
        owner_id = create_user("owner", "password123", "Tool Owner", "")
        borrower_id = create_user("borrower", "password123", "Tool Borrower", "")
        tool_id = ToolService.create_tool(
            owner_id, "Test Tool", "A test tool", "Power Tools", "good", []
        )
        
        # Create and complete reservation
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        two_days_ago = (date.today() - timedelta(days=2)).isoformat()
        
        # Create reservation directly with completed status
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO reservations (tool_id, borrower_id, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
            (tool_id, borrower_id, two_days_ago, yesterday, 'completed')
        )
        reservation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Test review eligibility
        can_review = ReviewService.can_review(reservation_id, borrower_id)
        assert can_review
        
        # Test non-participant can't review
        other_user = create_user("other", "password123", "Other User", "")
        cant_review = ReviewService.can_review(reservation_id, other_user)
        assert not cant_review
    
    def test_create_review(self, test_db):
        """Test review creation."""
        # Create users and tool
        owner_id = create_user("owner", "password123", "Tool Owner", "")
        borrower_id = create_user("borrower", "password123", "Tool Borrower", "")
        tool_id = ToolService.create_tool(
            owner_id, "Test Tool", "A test tool", "Power Tools", "good", []
        )
        
        # Create completed reservation
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        two_days_ago = (date.today() - timedelta(days=2)).isoformat()
        
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO reservations (tool_id, borrower_id, start_date, end_date, status) VALUES (?, ?, ?, ?, ?)",
            (tool_id, borrower_id, two_days_ago, yesterday, 'completed')
        )
        reservation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create review
        review_id = ReviewService.create_review(
            reservation_id, borrower_id, 5, "Great tool!"
        )
        assert review_id is not None
        
        # Test duplicate review
        duplicate_review = ReviewService.create_review(
            reservation_id, borrower_id, 4, "Another review"
        )
        assert duplicate_review is None

def test_database_initialization(test_db):
    """Test database initialization."""
    # Check that tables exist
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = {'users', 'tools', 'reservations', 'reviews', 'audit_logs'}
    assert expected_tables.issubset(set(tables))
    
    conn.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])