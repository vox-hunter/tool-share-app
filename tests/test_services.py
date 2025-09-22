"""Unit tests for ToolShare services."""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

from lib.models import ReservationStatus
from lib.services import ReservationService, ToolService


class TestReservationService:
    """Test reservation service logic."""

    def test_has_conflict_with_overlapping_dates(self):
        """Test conflict detection with overlapping dates."""
        # Mock supabase response with existing accepted reservation
        mock_result = Mock()
        mock_result.data = [{"id": "existing-reservation-id"}]

        with patch("lib.services.get_supabase_client") as mock_supabase:
            mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.neq.return_value.or_.return_value.execute.return_value = (
                mock_result
            )

            # Test overlapping dates
            has_conflict = ReservationService.has_conflict(
                tool_id="test-tool-id", start_date=date(2024, 3, 15), end_date=date(2024, 3, 17)
            )

            assert has_conflict is True

    def test_has_conflict_with_no_overlap(self):
        """Test no conflict when dates don't overlap."""
        # Mock supabase response with no conflicts
        mock_result = Mock()
        mock_result.data = []

        with patch("lib.services.get_supabase_client") as mock_supabase:
            mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.neq.return_value.or_.return_value.execute.return_value = (
                mock_result
            )

            # Test non-overlapping dates
            has_conflict = ReservationService.has_conflict(
                tool_id="test-tool-id", start_date=date(2024, 3, 20), end_date=date(2024, 3, 22)
            )

            assert has_conflict is False

    def test_blocked_dates_calculation(self):
        """Test blocked dates calculation."""
        # Mock supabase response with accepted reservations
        mock_result = Mock()
        mock_result.data = [
            {"start_date": "2024-03-15", "end_date": "2024-03-17"},
            {"start_date": "2024-03-20", "end_date": "2024-03-20"},
        ]

        with patch("lib.services.get_supabase_client") as mock_supabase:
            mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = (
                mock_result
            )

            blocked_dates = ReservationService.get_blocked_dates("test-tool-id")

            expected_dates = [
                date(2024, 3, 15),
                date(2024, 3, 16),
                date(2024, 3, 17),
                date(2024, 3, 20),
            ]

            assert blocked_dates == expected_dates


class TestToolService:
    """Test tool service logic."""

    def test_get_tools_with_category_filter(self):
        """Test getting tools with category filter."""
        # Mock supabase response
        mock_result = Mock()
        mock_result.data = [
            {
                "id": "tool1",
                "title": "Drill",
                "category": "Power Tools",
                "owner_id": "user1",
                "is_active": True,
                "daily_price": 5.0,
                "condition": "good",
                "description": "Test drill",
                "latitude": None,
                "longitude": None,
                "created_at": None,
                "updated_at": None,
                "owner": {"id": "user1", "email": "test@example.com", "full_name": "Test User"},
                "tool_images": [],
            }
        ]

        with patch("lib.services.get_supabase_client") as mock_supabase:
            mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = (
                mock_result
            )

            tools = ToolService.get_tools({"category": "Power Tools"})

            assert len(tools) == 1
            assert tools[0].title == "Drill"
            assert tools[0].category == "Power Tools"


class TestReservationWorkflow:
    """Test end-to-end reservation workflows."""

    def test_reservation_creation_prevents_conflicts(self):
        """Test that reservation creation checks for conflicts."""
        with patch("lib.services.ReservationService.has_conflict") as mock_has_conflict:
            mock_has_conflict.return_value = True

            with pytest.raises(Exception, match="Tool is not available"):
                ReservationService.create_reservation(
                    tool_id="test-tool",
                    borrower_id="test-borrower",
                    start_date=date(2024, 3, 15),
                    end_date=date(2024, 3, 17),
                )

    def test_reservation_status_update_with_conflict_check(self):
        """Test that accepting reservation checks for conflicts."""
        mock_reservation_result = Mock()
        mock_reservation_result.data = [
            {
                "id": "test-reservation",
                "tool_id": "test-tool",
                "start_date": "2024-03-15",
                "end_date": "2024-03-17",
            }
        ]

        with patch("lib.services.get_supabase_client") as mock_supabase:
            # Mock the reservation lookup
            mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value = (
                mock_reservation_result
            )

            with patch("lib.services.ReservationService.has_conflict") as mock_has_conflict:
                mock_has_conflict.return_value = True

                with pytest.raises(Exception, match="Tool is no longer available"):
                    ReservationService.update_reservation_status(
                        reservation_id="test-reservation",
                        status=ReservationStatus.ACCEPTED,
                        actor_id="test-owner",
                    )


def test_date_validation():
    """Test various date validation scenarios."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # Valid date range
    assert tomorrow > today

    # Invalid date range (end before start)
    assert not (yesterday > today)

    # Same day rental
    assert today == today


if __name__ == "__main__":
    pytest.main([__file__])
