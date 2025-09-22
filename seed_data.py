"""Seed data script for ToolShare application."""

import uuid
from datetime import date, timedelta

from lib.models import ReservationStatus, ToolCondition
from lib.supabase_client import get_supabase_client


def main():
    """Run the seed data script."""
    print("🌱 Seeding ToolShare database...")

    supabase = get_supabase_client()

    try:
        # Create users
        print("👥 Creating users...")
        users = create_sample_users(supabase)

        # Create tools
        print("🔧 Creating tools...")
        tools = create_sample_tools(supabase, users)

        # Create reservations
        print("📋 Creating reservations...")
        reservations = create_sample_reservations(supabase, tools, users)

        # Create reviews
        print("⭐ Creating reviews...")
        create_sample_reviews(supabase, reservations, users)

        print("✅ Database seeded successfully!")
        print(f"Created {len(users)} users, {len(tools)} tools, {len(reservations)} reservations")

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")


def create_sample_users(supabase):
    """Create sample users."""
    sample_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "alice.johnson@example.com",
            "full_name": "Alice Johnson",
            "bio": "DIY enthusiast and weekend warrior. Love working on home improvement projects!",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "bob.smith@example.com",
            "full_name": "Bob Smith",
            "bio": "Professional carpenter with a fully stocked workshop. Happy to share tools with neighbors.",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "carol.davis@example.com",
            "full_name": "Carol Davis",
            "bio": "Gardening expert and sustainable living advocate. Sharing is caring!",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "dave.wilson@example.com",
            "full_name": "Dave Wilson",
            "bio": "Tech consultant who loves gadgets and occasionally needs tools for projects.",
        },
        {
            "id": str(uuid.uuid4()),
            "email": "emma.brown@example.com",
            "full_name": "Emma Brown",
            "bio": "Art teacher and crafter. Always working on creative projects that need different tools.",
        },
    ]

    created_users = []
    for user_data in sample_users:
        try:
            result = supabase.table("users").insert(user_data).execute()
            if result.data:
                created_users.extend(result.data)
                print(f"  ✅ Created user: {user_data['full_name']}")
        except Exception as e:
            print(f"  ⚠️ User {user_data['email']} might already exist: {str(e)}")
            # Try to fetch existing user
            existing = supabase.table("users").select("*").eq("email", user_data["email"]).execute()
            if existing.data:
                created_users.extend(existing.data)

    return created_users


def create_sample_tools(supabase, users):
    """Create sample tools."""
    if len(users) < 3:
        print("⚠️ Need at least 3 users to create tools")
        return []

    sample_tools = [
        {
            "owner_id": users[0]["id"],  # Alice
            "title": "Cordless Power Drill",
            "description": "Black & Decker 18V cordless drill with multiple bits. Perfect for home projects and furniture assembly.",
            "category": "Power Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 5.00,
        },
        {
            "owner_id": users[1]["id"],  # Bob
            "title": "Circular Saw",
            "description": 'Professional-grade 7.25" circular saw. Great for cutting lumber and plywood. Safety gear included.',
            "category": "Power Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 10.00,
        },
        {
            "owner_id": users[2]["id"],  # Carol
            "title": "Garden Hose & Sprinkler Set",
            "description": "50ft garden hose with various spray attachments and rotating sprinkler. Perfect for lawn care.",
            "category": "Garden Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 0.00,
        },
        {
            "owner_id": users[0]["id"],  # Alice
            "title": "Ladder - 6ft Step",
            "description": "Sturdy aluminum step ladder. Great for painting, cleaning gutters, or reaching high places.",
            "category": "Home Improvement",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 3.00,
        },
        {
            "owner_id": users[3]["id"],  # Dave
            "title": "Digital Projector",
            "description": "HD projector perfect for outdoor movie nights or presentations. Includes screen and cables.",
            "category": "Electronics",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 15.00,
        },
        {
            "owner_id": users[4]["id"],  # Emma
            "title": "Sewing Machine",
            "description": "Brother computerized sewing machine with various stitches. Great for clothing alterations and crafts.",
            "category": "Other",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 8.00,
        },
        {
            "owner_id": users[1]["id"],  # Bob
            "title": "Miter Saw",
            "description": '10" compound miter saw for precise angle cuts. Perfect for trim work and framing.',
            "category": "Power Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 12.00,
        },
        {
            "owner_id": users[2]["id"],  # Carol
            "title": "Pressure Washer",
            "description": "Electric pressure washer for cleaning driveways, decks, and outdoor furniture.",
            "category": "Cleaning Equipment",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 7.00,
        },
        {
            "owner_id": users[0]["id"],  # Alice
            "title": "Tile Saw",
            "description": "Wet tile saw for bathroom and kitchen renovations. Includes diamond blade.",
            "category": "Power Tools",
            "condition": ToolCondition.FAIR.value,
            "daily_price": 15.00,
        },
        {
            "owner_id": users[4]["id"],  # Emma
            "title": "Stand Mixer",
            "description": "KitchenAid stand mixer with dough hook and whisk attachments. Perfect for baking projects.",
            "category": "Kitchen Appliances",
            "condition": ToolCondition.NEW.value,
            "daily_price": 6.00,
        },
        {
            "owner_id": users[3]["id"],  # Dave
            "title": "Socket Set - 120 Piece",
            "description": "Complete socket and wrench set with metric and standard sizes. Great for automotive work.",
            "category": "Hand Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 4.00,
        },
        {
            "owner_id": users[2]["id"],  # Carol
            "title": "Lawn Mower - Electric",
            "description": "Corded electric lawn mower, perfect for small to medium yards. Eco-friendly and quiet.",
            "category": "Garden Tools",
            "condition": ToolCondition.GOOD.value,
            "daily_price": 8.00,
        },
    ]

    created_tools = []
    for tool_data in sample_tools:
        try:
            result = supabase.table("tools").insert(tool_data).execute()
            if result.data:
                created_tools.extend(result.data)
                print(f"  ✅ Created tool: {tool_data['title']}")
        except Exception as e:
            print(f"  ❌ Failed to create tool {tool_data['title']}: {str(e)}")

    return created_tools


def create_sample_reservations(supabase, tools, users):
    """Create sample reservations."""
    if len(tools) < 5 or len(users) < 3:
        print("⚠️ Need at least 5 tools and 3 users to create reservations")
        return []

    today = date.today()

    sample_reservations = [
        {
            "tool_id": tools[0]["id"],  # Alice's drill
            "borrower_id": users[3]["id"],  # Dave borrows
            "start_date": (today + timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=3)).isoformat(),
            "status": ReservationStatus.ACCEPTED.value,
        },
        {
            "tool_id": tools[1]["id"],  # Bob's circular saw
            "borrower_id": users[4]["id"],  # Emma borrows
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": (today - timedelta(days=8)).isoformat(),
            "status": ReservationStatus.COMPLETED.value,
        },
        {
            "tool_id": tools[2]["id"],  # Carol's garden hose
            "borrower_id": users[0]["id"],  # Alice borrows
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "status": ReservationStatus.REQUESTED.value,
        },
        {
            "tool_id": tools[4]["id"],  # Dave's projector
            "borrower_id": users[1]["id"],  # Bob borrows
            "start_date": (today - timedelta(days=5)).isoformat(),
            "end_date": (today - timedelta(days=3)).isoformat(),
            "status": ReservationStatus.COMPLETED.value,
        },
        {
            "tool_id": tools[3]["id"],  # Alice's ladder
            "borrower_id": users[2]["id"],  # Carol borrows
            "start_date": (today - timedelta(days=1)).isoformat(),
            "end_date": today.isoformat(),
            "status": ReservationStatus.DECLINED.value,
        },
        {
            "tool_id": tools[5]["id"],  # Emma's sewing machine
            "borrower_id": users[3]["id"],  # Dave borrows
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=12)).isoformat(),
            "status": ReservationStatus.REQUESTED.value,
        },
    ]

    created_reservations = []
    for reservation_data in sample_reservations:
        try:
            result = supabase.table("reservations").insert(reservation_data).execute()
            if result.data:
                created_reservations.extend(result.data)
                print(f"  ✅ Created reservation: {reservation_data['status']}")
        except Exception as e:
            print(f"  ❌ Failed to create reservation: {str(e)}")

    return created_reservations


def create_sample_reviews(supabase, reservations, users):
    """Create sample reviews for completed reservations."""
    completed_reservations = [
        r for r in reservations if r["status"] == ReservationStatus.COMPLETED.value
    ]

    if not completed_reservations:
        print("  ⚠️ No completed reservations to review")
        return []

    sample_reviews = [
        {
            "reservation_id": completed_reservations[0]["id"],
            "reviewer_id": completed_reservations[0]["borrower_id"],
            "rating": 5,
            "comment": "Excellent tool! Works perfectly and Bob was very helpful with instructions.",
        },
        {
            "reservation_id": completed_reservations[1]["id"]
            if len(completed_reservations) > 1
            else completed_reservations[0]["id"],
            "reviewer_id": completed_reservations[1]["borrower_id"]
            if len(completed_reservations) > 1
            else completed_reservations[0]["borrower_id"],
            "rating": 4,
            "comment": "Great projector for movie night! Easy pickup and return process.",
        },
    ]

    created_reviews = []
    for review_data in sample_reviews:
        try:
            result = supabase.table("reviews").insert(review_data).execute()
            if result.data:
                created_reviews.extend(result.data)
                print(f"  ✅ Created review: {review_data['rating']} stars")
        except Exception as e:
            print(f"  ❌ Failed to create review: {str(e)}")

    return created_reviews


if __name__ == "__main__":
    main()
