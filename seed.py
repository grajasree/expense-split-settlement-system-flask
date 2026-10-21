"""
Seed Script for Expense Split and Settlement System
Populates the database with realistic sample data for academic demonstration and testing.
"""
from decimal import Decimal
from werkzeug.security import generate_password_hash
from db import get_db_connection, init_db
from config import Config

def seed_database():
    print(f"Connecting to database '{Config.DB_NAME}'...")
    # Ensure database and schema exist
    init_db()

    conn = get_db_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            # Check if users already exist
            cursor.execute("SELECT COUNT(*) AS cnt FROM users")
            if cursor.fetchone()['cnt'] > 0:
                print("Database already contains data. Clearing existing sample records for fresh seed...")
                cursor.execute("DELETE FROM expense_splits")
                cursor.execute("DELETE FROM expenses")
                cursor.execute("DELETE FROM group_budgets")
                cursor.execute("DELETE FROM group_members")
                cursor.execute("DELETE FROM `groups`")
                cursor.execute("DELETE FROM users")

            print("Creating sample users...")
            pw_hash = generate_password_hash("password123")
            users_data = [
                ("Rahul Sharma", "rahul@example.com", pw_hash),
                ("Priya Patel", "priya@example.com", pw_hash),
                ("Amit Kumar", "amit@example.com", pw_hash),
                ("Sneha Rao", "sneha@example.com", pw_hash),
            ]
            cursor.executemany("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", users_data)

            # Get user IDs
            cursor.execute("SELECT id, email FROM users")
            user_map = {r['email']: r['id'] for r in cursor.fetchall()}
            u_rahul = user_map["rahul@example.com"]
            u_priya = user_map["priya@example.com"]
            u_amit = user_map["amit@example.com"]
            u_sneha = user_map["sneha@example.com"]

            print("Creating sample groups & budgets...")
            # Group 1: Flatmates (Monthly Budget: 20000)
            cursor.execute(
                "INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)",
                ("Apartment 402 - Flatmates", "Shared apartment rent, groceries, and utility bills", u_rahul)
            )
            g_flat = cursor.lastrowid
            cursor.execute("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (g_flat, Decimal('20000.00')))

            # Group 2: Goa Trip (Monthly Budget: 15000)
            cursor.execute(
                "INSERT INTO `groups` (name, description, created_by) VALUES (%s, %s, %s)",
                ("Weekend Goa Trip", "Travel, resort, beach dining, and scooter rentals", u_priya)
            )
            g_trip = cursor.lastrowid
            cursor.execute("INSERT INTO group_budgets (group_id, monthly_budget) VALUES (%s, %s)", (g_trip, Decimal('15000.00')))

            # Add members to groups
            flat_members = [
                (g_flat, u_rahul, 'creator'),
                (g_flat, u_priya, 'member'),
                (g_flat, u_amit, 'member'),
            ]
            trip_members = [
                (g_trip, u_priya, 'creator'),
                (g_trip, u_rahul, 'member'),
                (g_trip, u_amit, 'member'),
                (g_trip, u_sneha, 'member'),
            ]
            cursor.executemany("INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, %s)", flat_members + trip_members)

            print("Creating sample expenses with Equal, Percentage, and Custom splits...")

            # Expense 1: Flat Groceries (Equal Split among 3: Rahul, Priya, Amit) = 3000
            cursor.execute("""
                INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                VALUES (%s, %s, %s, %s, %s, '2026-10-05', 'EQUAL')
            """, (g_flat, u_rahul, "Monthly Supermarket Groceries", Decimal('3000.00'), "Groceries"))
            e1 = cursor.lastrowid
            cursor.executemany("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (%s, %s, %s, %s)", [
                (e1, u_rahul, Decimal('1000.00'), 33.33),
                (e1, u_priya, Decimal('1000.00'), 33.33),
                (e1, u_amit, Decimal('1000.00'), 33.33),
            ])

            # Expense 2: WiFi and Electricity (Equal Split: Priya paid 1800)
            cursor.execute("""
                INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                VALUES (%s, %s, %s, %s, %s, '2026-10-08', 'EQUAL')
            """, (g_flat, u_priya, "Electricity & High-Speed WiFi Bill", Decimal('1800.00'), "Utilities & Bills"))
            e2 = cursor.lastrowid
            cursor.executemany("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (%s, %s, %s, %s)", [
                (e2, u_rahul, Decimal('600.00'), 33.33),
                (e2, u_priya, Decimal('600.00'), 33.33),
                (e2, u_amit, Decimal('600.00'), 33.33),
            ])

            # Expense 3: Living Room AC Service (Percentage Split: Amit paid 4000, 50% Rahul, 30% Priya, 20% Amit)
            cursor.execute("""
                INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                VALUES (%s, %s, %s, %s, %s, '2026-10-12', 'PERCENTAGE')
            """, (g_flat, u_amit, "Living Room AC Deep Service & Maintenance", Decimal('4000.00'), "Housing & Rent"))
            e3 = cursor.lastrowid
            cursor.executemany("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (%s, %s, %s, %s)", [
                (e3, u_rahul, Decimal('2000.00'), 50.00),
                (e3, u_priya, Decimal('1200.00'), 30.00),
                (e3, u_amit, Decimal('800.00'), 20.00),
            ])

            # Expense 4: Goa Beach Resort Booking (Custom Split: Priya paid 9000 among 4 members)
            cursor.execute("""
                INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                VALUES (%s, %s, %s, %s, %s, '2026-10-15', 'CUSTOM')
            """, (g_trip, u_priya, "Beachside Villa 2-Night Booking", Decimal('9000.00'), "Travel"))
            e4 = cursor.lastrowid
            cursor.executemany("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (%s, %s, %s, %s)", [
                (e4, u_priya, Decimal('2500.00'), None),
                (e4, u_rahul, Decimal('2500.00'), None),
                (e4, u_amit, Decimal('2000.00'), None),
                (e4, u_sneha, Decimal('2000.00'), None),
            ])

            # Expense 5: Goa Seafood Dinner (Equal Split: Sneha paid 3600 among 4)
            cursor.execute("""
                INSERT INTO expenses (group_id, paid_by, description, amount, category, date, split_type)
                VALUES (%s, %s, %s, %s, %s, '2026-10-17', 'EQUAL')
            """, (g_trip, u_sneha, "Fisherman's Wharf Seafood Dinner", Decimal('3600.00'), "Food & Dining"))
            e5 = cursor.lastrowid
            cursor.executemany("INSERT INTO expense_splits (expense_id, user_id, share_amount, share_percentage) VALUES (%s, %s, %s, %s)", [
                (e5, u_priya, Decimal('900.00'), 25.00),
                (e5, u_rahul, Decimal('900.00'), 25.00),
                (e5, u_amit, Decimal('900.00'), 25.00),
                (e5, u_sneha, Decimal('900.00'), 25.00),
            ])

        conn.commit()
        print("Database seeding completed successfully!")
        print("\nTest User Credentials:")
        print("1. Email: rahul@example.com  | Password: password123")
        print("2. Email: priya@example.com  | Password: password123")
        print("3. Email: amit@example.com   | Password: password123")
        print("4. Email: sneha@example.com  | Password: password123")
    finally:
        conn.close()

if __name__ == '__main__':
    seed_database()
