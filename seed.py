"""
seed.py — CargoConnect test data seeder
========================================
Sprint task 2.4: populate the database with a realistic baseline dataset.

Seed contents
-------------
- 1 admin user
- 2 customers (each with a User account)
- 3 drivers  (2 verified, 1 unverified — each with a User account and a Truck)
- 2 bookings  (1 pending, 1 completed)
- 1 payment   (linked to the completed booking)
- 1 rating    (linked to the completed booking)
- 3 notifications (one per relevant user)

Usage (after `flask db upgrade` has been run):
    python seed.py
"""

from datetime import datetime, timedelta
from app import create_app
from extensions import db, bcrypt

from models.user import User
from models.customer import Customer
from models.driver import Driver
from models.truck import Truck
from models.booking import Booking
from models.payment import Payment
from models.rating import Rating
from models.notification import Notification


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _hash(plain: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return bcrypt.generate_password_hash(plain).decode("utf-8")


# ---------------------------------------------------------------------------
# main seeder
# ---------------------------------------------------------------------------

def seed():
    app = create_app()

    with app.app_context():
        # ------------------------------------------------------------------ #
        # 0. wipe existing seed data (safe to re-run)                         #
        # ------------------------------------------------------------------ #
        print("Clearing old seed data …")
        # Delete in reverse dependency order to respect FK constraints
        Notification.query.delete()
        Rating.query.delete()
        Payment.query.delete()
        Booking.query.delete()
        Truck.query.delete()
        Driver.query.delete()
        Customer.query.delete()
        User.query.delete()
        db.session.commit()
        print("  ✓ Cleared.")

        # ------------------------------------------------------------------ #
        # 1. Users                                                             #
        # ------------------------------------------------------------------ #
        print("Creating users …")

        admin_user = User(
            user_name="Admin CargoConnect",
            email="admin@cargoconnect.rw",
            user_phone_no="+250780000001",
            password_hash=_hash("Admin@1234"),
            role="admin",
        )

        customer_user_1 = User(
            user_name="Alice Uwase",
            email="alice@example.rw",
            user_phone_no="+250780000002",
            password_hash=_hash("Alice@1234"),
            role="customer",
        )

        customer_user_2 = User(
            user_name="Bob Mugisha",
            email="bob@example.rw",
            user_phone_no="+250780000003",
            password_hash=_hash("Bob@1234"),
            role="customer",
        )

        driver_user_1 = User(
            user_name="Jean-Pierre Habimana",
            email="jp@example.rw",
            user_phone_no="+250780000004",
            password_hash=_hash("Driver@1234"),
            role="driver",
        )

        driver_user_2 = User(
            user_name="Marie Mukamana",
            email="marie@example.rw",
            user_phone_no="+250780000005",
            password_hash=_hash("Driver@1234"),
            role="driver",
        )

        # Unverified driver — should see "pending verification" banner
        driver_user_3 = User(
            user_name="Eric Nshimyimana",
            email="eric@example.rw",
            user_phone_no="+250780000006",
            password_hash=_hash("Driver@1234"),
            role="driver",
        )

        db.session.add_all([
            admin_user,
            customer_user_1, customer_user_2,
            driver_user_1, driver_user_2, driver_user_3,
        ])
        db.session.flush()   # get auto-generated IDs before proceeding
        print("  ✓ 6 users.")

        # ------------------------------------------------------------------ #
        # 2. Customer profiles                                                 #
        # ------------------------------------------------------------------ #
        print("Creating customer profiles …")

        customer_1 = Customer(
            user_id=customer_user_1.user_id,
            default_address="KG 11 Ave, Kigali",
        )
        customer_2 = Customer(
            user_id=customer_user_2.user_id,
            default_address="KN 5 Rd, Kigali",
        )

        db.session.add_all([customer_1, customer_2])
        db.session.flush()
        print("  ✓ 2 customers.")

        # ------------------------------------------------------------------ #
        # 3. Driver profiles                                                   #
        # Kigali city-centre coordinates: -1.9441, 30.0619                    #
        # ------------------------------------------------------------------ #
        print("Creating driver profiles …")

        driver_1 = Driver(
            user_id=driver_user_1.user_id,
            licence_no="RW-LIC-001",
            rating=4.5,
            is_available=True,
            is_verified=True,
            # Slightly north-west of Kigali centre
            latitude=-1.9400,
            longitude=30.0580,
        )
        driver_2 = Driver(
            user_id=driver_user_2.user_id,
            licence_no="RW-LIC-002",
            rating=3.8,
            is_available=False,
            is_verified=True,
            # Slightly south of Kigali centre
            latitude=-1.9500,
            longitude=30.0650,
        )
        driver_3 = Driver(
            user_id=driver_user_3.user_id,
            licence_no="RW-LIC-003",
            rating=0.0,
            is_available=False,
            is_verified=False,   # ← pending verification
            latitude=None,
            longitude=None,
        )

        db.session.add_all([driver_1, driver_2, driver_3])
        db.session.flush()
        print("  ✓ 3 drivers (1 unverified).")

        # ------------------------------------------------------------------ #
        # 4. Trucks                                                            #
        # ------------------------------------------------------------------ #
        print("Creating trucks …")

        truck_1 = Truck(
            driver_id=driver_1.driver_id,
            plate_no="RAB 123 A",
            capacity=5.0,   # 5 tons
        )
        truck_2 = Truck(
            driver_id=driver_2.driver_id,
            plate_no="RAC 456 B",
            capacity=3.0,   # 3 tons
        )
        truck_3 = Truck(
            driver_id=driver_3.driver_id,
            plate_no="RAD 789 C",
            capacity=10.0,  # 10 tons — unverified driver
        )

        db.session.add_all([truck_1, truck_2, truck_3])
        db.session.flush()
        print("  ✓ 3 trucks.")

        # ------------------------------------------------------------------ #
        # 5. Bookings                                                          #
        # ------------------------------------------------------------------ #
        print("Creating bookings …")

        # Booking 1 — PENDING (customer_1 booked driver_1, scheduled tomorrow)
        booking_pending = Booking(
            customer_id=customer_1.customer_id,
            truck_id=truck_1.truck_id,
            driver_id=driver_1.driver_id,
            pickup_address="KG 11 Ave, Kigali",
            dropoff_address="KK 15 Rd, Kicukiro, Kigali",
            scheduled_time=datetime.utcnow() + timedelta(days=1),
            estimated_cost=12500.00,
            status="pending",
        )

        # Booking 2 — COMPLETED (customer_2 booked driver_2, completed yesterday)
        booking_completed = Booking(
            customer_id=customer_2.customer_id,
            truck_id=truck_2.truck_id,
            driver_id=driver_2.driver_id,
            pickup_address="KN 5 Rd, Nyarugenge, Kigali",
            dropoff_address="KG 9 Ave, Gasabo, Kigali",
            scheduled_time=datetime.utcnow() - timedelta(days=1),
            estimated_cost=9800.00,
            status="completed",
        )

        db.session.add_all([booking_pending, booking_completed])
        db.session.flush()
        print("  ✓ 2 bookings (1 pending, 1 completed).")

        # ------------------------------------------------------------------ #
        # 6. Payment  (for the completed booking)                             #
        # ------------------------------------------------------------------ #
        print("Creating payment …")

        payment = Payment(
            booking_id=booking_completed.booking_id,
            amount=9800.00,
            method="MoMo",
            status="paid",
            paid_at=datetime.utcnow() - timedelta(hours=20),
        )

        db.session.add(payment)
        db.session.flush()
        print("  ✓ 1 payment (paid via MoMo).")

        # ------------------------------------------------------------------ #
        # 7. Rating  (customer_2 rates driver_2 after completed booking)      #
        # ------------------------------------------------------------------ #
        print("Creating rating …")

        rating = Rating(
            booking_id=booking_completed.booking_id,
            customer_id=customer_2.customer_id,
            driver_id=driver_2.driver_id,
            rating_score=4.0,
            comment="Good service, arrived on time.",
        )

        db.session.add(rating)
        db.session.flush()
        print("  ✓ 1 rating (4.0 stars).")

        # ------------------------------------------------------------------ #
        # 8. Notifications                                                     #
        # ------------------------------------------------------------------ #
        print("Creating notifications …")

        notif_1 = Notification(
            user_id=customer_user_1.user_id,
            message="Your booking has been created and is awaiting driver confirmation.",
            channel="in_app",
            is_read=False,
        )
        notif_2 = Notification(
            user_id=driver_user_1.user_id,
            message="You have a new job request. Please review and accept or decline.",
            channel="in_app",
            is_read=False,
        )
        notif_3 = Notification(
            user_id=customer_user_2.user_id,
            message="Your trip has been completed. Please rate your driver.",
            channel="in_app",
            is_read=True,
        )

        db.session.add_all([notif_1, notif_2, notif_3])
        db.session.flush()
        print("  ✓ 3 notifications.")

        # ------------------------------------------------------------------ #
        # 9. Commit everything                                                 #
        # ------------------------------------------------------------------ #
        db.session.commit()

        # ------------------------------------------------------------------ #
        # 10. Summary                                                          #
        # ------------------------------------------------------------------ #
        print("\n" + "=" * 55)
        print("  Seed complete — database is ready for demo.")
        print("=" * 55)
        print(f"\n  Admin login   : admin@cargoconnect.rw  /  Admin@1234")
        print(f"  Customer 1    : alice@example.rw       /  Alice@1234")
        print(f"  Customer 2    : bob@example.rw         /  Bob@1234")
        print(f"  Driver 1 ✓    : jp@example.rw          /  Driver@1234")
        print(f"  Driver 2 ✓    : marie@example.rw       /  Driver@1234")
        print(f"  Driver 3 ✗    : eric@example.rw        /  Driver@1234  (unverified)")
        print()


if __name__ == "__main__":
    seed()
