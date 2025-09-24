"""
Seed data script for ToolShare application.
Populates the database with demo users, tools, and reservations.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.db import init_database, get_connection
from lib.auth import create_user
from lib.services import ToolService, ReservationService, ReviewService
import json
from datetime import datetime, timedelta, date

def create_seed_users():
    """Create demo users."""
    print("Creating seed users...")
    
    users = [
        {
            "username": "admin",
            "password": "admin123",
            "full_name": "System Administrator",
            "bio": "ToolShare system administrator. Here to help the community!"
        },
        {
            "username": "alice_builder",
            "password": "password123",
            "full_name": "Alice Johnson",
            "bio": "DIY enthusiast and home improvement expert. Love building and fixing things!"
        },
        {
            "username": "bob_gardener",
            "password": "password123",
            "full_name": "Bob Smith",
            "bio": "Passionate gardener with a green thumb. Happy to share garden tools with neighbors."
        },
        {
            "username": "carol_chef",
            "password": "password123",
            "full_name": "Carol Davis",
            "bio": "Professional chef who loves trying new kitchen gadgets and sharing them."
        },
        {
            "username": "david_mechanic",
            "password": "password123",
            "full_name": "David Wilson",
            "bio": "Automotive enthusiast and weekend mechanic. Owns lots of specialized tools."
        }
    ]
    
    user_ids = []
    for user_data in users:
        user_id = create_user(
            user_data["username"],
            user_data["password"],
            user_data["full_name"],
            user_data["bio"]
        )
        if user_id:
            user_ids.append(user_id)
            print(f"Created user: {user_data['username']} (ID: {user_id})")
        else:
            print(f"Failed to create user: {user_data['username']}")
    
    return user_ids

def create_seed_tools(user_ids):
    """Create demo tools."""
    print("Creating seed tools...")
    
    tools = [
        # Alice's tools (Power Tools)
        {
            "owner_id": user_ids[1],  # alice_builder
            "title": "Cordless Drill Set",
            "description": "High-quality cordless drill with various bits and attachments. Perfect for home improvement projects.",
            "category": "Power Tools",
            "condition": "good",
            "image_paths": []
        },
        {
            "owner_id": user_ids[1],
            "title": "Circular Saw",
            "description": "Professional-grade circular saw for woodworking. Safety glasses included.",
            "category": "Power Tools",
            "condition": "good",
            "image_paths": []
        },
        {
            "owner_id": user_ids[1],
            "title": "Paint Sprayer",
            "description": "Electric paint sprayer for interior and exterior projects. Much faster than brush painting!",
            "category": "Home Improvement",
            "condition": "fair",
            "image_paths": []
        },
        
        # Bob's tools (Garden Tools)
        {
            "owner_id": user_ids[2],  # bob_gardener
            "title": "Lawn Mower",
            "description": "Self-propelled gas lawn mower. Excellent for medium to large yards.",
            "category": "Garden Tools",
            "condition": "good",
            "image_paths": []
        },
        {
            "owner_id": user_ids[2],
            "title": "Hedge Trimmer",
            "description": "Electric hedge trimmer for shaping bushes and hedges. Very easy to use.",
            "category": "Garden Tools",
            "condition": "new",
            "image_paths": []
        },
        {
            "owner_id": user_ids[2],
            "title": "Pressure Washer",
            "description": "High-pressure washer for cleaning driveways, decks, and outdoor furniture.",
            "category": "Cleaning",
            "condition": "good",
            "image_paths": []
        },
        
        # Carol's tools (Kitchen)
        {
            "owner_id": user_ids[3],  # carol_chef
            "title": "Stand Mixer",
            "description": "Professional KitchenAid stand mixer with multiple attachments. Perfect for baking.",
            "category": "Kitchen Appliances",
            "condition": "new",
            "image_paths": []
        },
        {
            "owner_id": user_ids[3],
            "title": "Food Processor",
            "description": "Large capacity food processor with various blades. Great for meal prep.",
            "category": "Kitchen Appliances",
            "condition": "good",
            "image_paths": []
        },
        {
            "owner_id": user_ids[3],
            "title": "Dehydrator",
            "description": "Electric food dehydrator for making dried fruits, jerky, and herbs.",
            "category": "Kitchen Appliances",
            "condition": "good",
            "image_paths": []
        },
        
        # David's tools (Automotive)
        {
            "owner_id": user_ids[4],  # david_mechanic
            "title": "Car Jack Set",
            "description": "Heavy-duty hydraulic car jack with jack stands. Essential for car maintenance.",
            "category": "Automotive",
            "condition": "good",
            "image_paths": []
        },
        {
            "owner_id": user_ids[4],
            "title": "Socket Wrench Set",
            "description": "Complete socket wrench set with metric and standard sizes. Professional quality.",
            "category": "Hand Tools",
            "condition": "new",
            "image_paths": []
        },
        {
            "owner_id": user_ids[4],
            "title": "Tire Pressure Gauge",
            "description": "Digital tire pressure gauge for accurate readings. Battery operated.",
            "category": "Automotive",
            "condition": "new",
            "image_paths": []
        }
    ]
    
    tool_ids = []
    for tool_data in tools:
        tool_id = ToolService.create_tool(
            tool_data["owner_id"],
            tool_data["title"],
            tool_data["description"],
            tool_data["category"],
            tool_data["condition"],
            tool_data["image_paths"]
        )
        if tool_id:
            tool_ids.append(tool_id)
            print(f"Created tool: {tool_data['title']} (ID: {tool_id})")
        else:
            print(f"Failed to create tool: {tool_data['title']}")
    
    return tool_ids

def create_seed_reservations(user_ids, tool_ids):
    """Create demo reservations."""
    print("Creating seed reservations...")
    
    today = date.today()
    
    reservations = [
        # Past completed reservations
        {
            "tool_id": tool_ids[0],  # Cordless Drill
            "borrower_id": user_ids[2],  # Bob
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": (today - timedelta(days=8)).isoformat(),
            "status": "completed"
        },
        {
            "tool_id": tool_ids[3],  # Lawn Mower
            "borrower_id": user_ids[1],  # Alice
            "start_date": (today - timedelta(days=5)).isoformat(),
            "end_date": (today - timedelta(days=3)).isoformat(),
            "status": "completed"
        },
        
        # Current accepted reservations
        {
            "tool_id": tool_ids[4],  # Hedge Trimmer
            "borrower_id": user_ids[4],  # David
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=2)).isoformat(),
            "status": "accepted"
        },
        
        # Future accepted reservations
        {
            "tool_id": tool_ids[1],  # Circular Saw
            "borrower_id": user_ids[3],  # Carol
            "start_date": (today + timedelta(days=3)).isoformat(),
            "end_date": (today + timedelta(days=5)).isoformat(),
            "status": "accepted"
        },
        
        # Pending reservations
        {
            "tool_id": tool_ids[5],  # Pressure Washer
            "borrower_id": user_ids[1],  # Alice
            "start_date": (today + timedelta(days=7)).isoformat(),
            "end_date": (today + timedelta(days=9)).isoformat(),
            "status": "requested"
        },
        {
            "tool_id": tool_ids[2],  # Paint Sprayer
            "borrower_id": user_ids[2],  # Bob
            "start_date": (today + timedelta(days=14)).isoformat(),
            "end_date": (today + timedelta(days=16)).isoformat(),
            "status": "requested"
        }
    ]
    
    reservation_ids = []
    conn = get_connection()
    
    try:
        for res_data in reservations:
            # Create reservation directly in database to set custom status
            cursor = conn.execute(
                """INSERT INTO reservations (tool_id, borrower_id, start_date, end_date, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (res_data["tool_id"], res_data["borrower_id"], 
                 res_data["start_date"], res_data["end_date"], res_data["status"])
            )
            reservation_id = cursor.lastrowid
            reservation_ids.append(reservation_id)
            print(f"Created reservation: {reservation_id} ({res_data['status']})")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error creating reservations: {e}")
    finally:
        conn.close()
    
    return reservation_ids

def create_seed_reviews(user_ids, reservation_ids):
    """Create demo reviews for completed reservations."""
    print("Creating seed reviews...")
    
    reviews = [
        {
            "reservation_id": reservation_ids[0],  # Bob's review of Alice's drill
            "reviewer_id": user_ids[2],  # Bob
            "rating": 5,
            "comment": "Excellent drill! Alice was very helpful and the tool was in perfect condition."
        },
        {
            "reservation_id": reservation_ids[1],  # Alice's review of Bob's lawn mower
            "reviewer_id": user_ids[1],  # Alice
            "rating": 4,
            "comment": "Great lawn mower, started right up and cut evenly. Thanks Bob!"
        }
    ]
    
    for review_data in reviews:
        review_id = ReviewService.create_review(
            review_data["reservation_id"],
            review_data["reviewer_id"],
            review_data["rating"],
            review_data["comment"]
        )
        if review_id:
            print(f"Created review: {review_id}")
        else:
            print(f"Failed to create review for reservation {review_data['reservation_id']}")

def main():
    """Main seed function."""
    print("🌱 Seeding ToolShare database...")
    
    # Initialize database
    init_database()
    
    # Create seed data
    user_ids = create_seed_users()
    if len(user_ids) < 5:
        print("❌ Failed to create all users. Aborting seed.")
        return
    
    tool_ids = create_seed_tools(user_ids)
    if len(tool_ids) < 12:
        print("❌ Failed to create all tools. Continuing with available tools.")
    
    reservation_ids = create_seed_reservations(user_ids, tool_ids[:6])  # Use first 6 tools
    
    create_seed_reviews(user_ids, reservation_ids)
    
    print("\n✅ Seed data created successfully!")
    print("\n📊 Summary:")
    print(f"Users: {len(user_ids)}")
    print(f"Tools: {len(tool_ids)}")
    print(f"Reservations: {len(reservation_ids)}")
    print("\n👤 Demo Login Accounts:")
    print("Admin: admin / admin123")
    print("Alice: alice_builder / password123")
    print("Bob: bob_gardener / password123")
    print("Carol: carol_chef / password123")
    print("David: david_mechanic / password123")

if __name__ == "__main__":
    main()