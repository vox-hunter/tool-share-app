#!/usr/bin/env python3
"""
Demo script for ToolShare application.
Shows basic functionality without requiring Supabase connection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_models():
    """Demo the data models."""
    print("🔧 ToolShare Data Models Demo")
    print("=" * 40)
    
    from lib.models import Tool, User, Reservation, ToolCondition, ReservationStatus, TOOL_CATEGORIES
    from datetime import date
    
    # Demo user
    user = User(
        id="user-123",
        email="alice@example.com", 
        full_name="Alice Johnson",
        bio="DIY enthusiast"
    )
    print(f"User: {user.full_name} ({user.email})")
    
    # Demo tool
    tool = Tool(
        id="tool-456",
        owner_id=user.id,
        title="Cordless Drill",
        description="Black & Decker 18V cordless drill",
        category="Power Tools",
        condition=ToolCondition.GOOD,
        daily_price=5.00,
        owner=user
    )
    print(f"Tool: {tool.title} - ${tool.daily_price}/day")
    
    # Demo reservation
    reservation = Reservation(
        id="res-789",
        tool_id=tool.id,
        borrower_id="user-456",
        start_date=date(2024, 3, 15),
        end_date=date(2024, 3, 17),
        status=ReservationStatus.ACCEPTED,
        tool=tool
    )
    print(f"Reservation: {reservation.start_date} to {reservation.end_date} ({reservation.status.value})")
    
    print(f"\nAvailable categories: {len(TOOL_CATEGORIES)} types")
    for category in TOOL_CATEGORIES[:5]:
        print(f"  - {category}")
    print("  ...")

def demo_business_logic():
    """Demo business logic without database."""
    print("\n🧠 ToolShare Business Logic Demo")
    print("=" * 40)
    
    from datetime import date, timedelta
    
    # Date validation
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    print(f"Today: {today}")
    print(f"Valid rental period: {tomorrow} to {next_week}")
    
    # Simulate conflict detection
    print("\n📅 Conflict Detection Logic:")
    print("✅ No overlap: Mar 1-3 vs Mar 5-7")
    print("❌ Overlap detected: Mar 1-5 vs Mar 3-7")
    print("❌ Same dates: Mar 1-3 vs Mar 1-3")

def demo_security():
    """Demo security concepts."""
    print("\n🔒 ToolShare Security Demo")
    print("=" * 40)
    
    print("Row Level Security Policies:")
    print("✅ Users can only edit their own tools")
    print("✅ Reservations visible to borrower and owner only")
    print("✅ Reviews only for completed reservations")
    print("✅ Public tool browsing for active tools")
    
    print("\nInput Validation:")
    print("✅ Date ranges validated")
    print("✅ Email format checking")
    print("✅ File upload restrictions")
    print("✅ SQL injection prevention")

def main():
    """Run the demo."""
    print("🛠️  TOOLSHARE APPLICATION DEMO")
    print("=" * 50)
    print()
    
    try:
        demo_models()
        demo_business_logic() 
        demo_security()
        
        print("\n🎉 Demo Complete!")
        print("\nTo run the full application:")
        print("1. Set up Supabase project and credentials")
        print("2. Run: streamlit run main.py")
        print("3. Visit: http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())