"""
seed.py — populate the database with demo drivers and realistic booking data.
Run once from the project root:

    python3 seed.py

Safe to re-run: skips any record that already exists.
"""
import eventlet
eventlet.monkey_patch()

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from decimal import Decimal
import random

from app import app
from extensions import db, bcrypt
from models.user import User
from models.driver import Driver
from models.customer import Customer
from models.truck import Truck
from models.booking import Booking
from models.payment import Payment
from models.rating import Rating


# ─────────────────────────────────────────────
#  25 demo drivers spread across Kigali
# ─────────────────────────────────────────────
DEMO_DRIVERS = [
    {"user_name": "Jean Paul Habimana",       "email": "driver1@demo.rw",  "user_phone_no": "250788100001", "password": "demo1234", "licence_no": "RW-DL-110001", "latitude": -1.9500, "longitude": 30.0580, "rating": 4.8, "plate_no": "RAA 001 A", "capacity": 3.0},
    {"user_name": "Marie Claire Uwase",       "email": "driver2@demo.rw",  "user_phone_no": "250788100002", "password": "demo1234", "licence_no": "RW-DL-110002", "latitude": -1.9350, "longitude": 30.0700, "rating": 4.5, "plate_no": "RAB 002 B", "capacity": 5.0},
    {"user_name": "Emmanuel Nzeyimana",       "email": "driver3@demo.rw",  "user_phone_no": "250788100003", "password": "demo1234", "licence_no": "RW-DL-110003", "latitude": -1.9600, "longitude": 30.0500, "rating": 4.2, "plate_no": "RAC 003 C", "capacity": 2.0},
    {"user_name": "Aline Mukamana",           "email": "driver4@demo.rw",  "user_phone_no": "250788100004", "password": "demo1234", "licence_no": "RW-DL-110004", "latitude": -1.9200, "longitude": 30.0800, "rating": 4.9, "plate_no": "RAD 004 D", "capacity": 8.0},
    {"user_name": "Patrick Bizimana",         "email": "driver5@demo.rw",  "user_phone_no": "250788100005", "password": "demo1234", "licence_no": "RW-DL-110005", "latitude": -1.9441, "longitude": 30.0619, "rating": 3.9, "plate_no": "RAE 005 E", "capacity": 1.5},
    {"user_name": "Claudine Umubyeyi",        "email": "driver6@demo.rw",  "user_phone_no": "250788100006", "password": "demo1234", "licence_no": "RW-DL-110006", "latitude": -1.9300, "longitude": 30.0550, "rating": 4.7, "plate_no": "RAF 006 F", "capacity": 4.0},
    {"user_name": "Innocent Nshimiyimana",    "email": "driver7@demo.rw",  "user_phone_no": "250788100007", "password": "demo1234", "licence_no": "RW-DL-110007", "latitude": -1.9550, "longitude": 30.0750, "rating": 4.1, "plate_no": "RAG 007 G", "capacity": 6.0},
    {"user_name": "Vestine Ingabire",         "email": "driver8@demo.rw",  "user_phone_no": "250788100008", "password": "demo1234", "licence_no": "RW-DL-110008", "latitude": -1.9150, "longitude": 30.0650, "rating": 4.6, "plate_no": "RAH 008 H", "capacity": 2.5},
    {"user_name": "Faustin Nkurunziza",       "email": "driver9@demo.rw",  "user_phone_no": "250788100009", "password": "demo1234", "licence_no": "RW-DL-110009", "latitude": -1.9650, "longitude": 30.0450, "rating": 3.8, "plate_no": "RAI 009 I", "capacity": 10.0},
    {"user_name": "Solange Mutesi",           "email": "driver10@demo.rw", "user_phone_no": "250788100010", "password": "demo1234", "licence_no": "RW-DL-110010", "latitude": -1.9400, "longitude": 30.0900, "rating": 4.4, "plate_no": "RAJ 010 J", "capacity": 3.5},
    {"user_name": "Theogene Hakizimana",      "email": "driver11@demo.rw", "user_phone_no": "250788100011", "password": "demo1234", "licence_no": "RW-DL-110011", "latitude": -1.9250, "longitude": 30.0480, "rating": 4.3, "plate_no": "RAK 011 K", "capacity": 1.5},
    {"user_name": "Beatrice Uwineza",         "email": "driver12@demo.rw", "user_phone_no": "250788100012", "password": "demo1234", "licence_no": "RW-DL-110012", "latitude": -1.9700, "longitude": 30.0620, "rating": 4.9, "plate_no": "RAL 012 L", "capacity": 7.0},
    {"user_name": "Alexis Munyaneza",         "email": "driver13@demo.rw", "user_phone_no": "250788100013", "password": "demo1234", "licence_no": "RW-DL-110013", "latitude": -1.9100, "longitude": 30.0730, "rating": 4.0, "plate_no": "RAM 013 M", "capacity": 2.0},
    {"user_name": "Clarisse Nyirahabimana",   "email": "driver14@demo.rw", "user_phone_no": "250788100014", "password": "demo1234", "licence_no": "RW-DL-110014", "latitude": -1.9380, "longitude": 30.0560, "rating": 4.5, "plate_no": "RAN 014 N", "capacity": 5.0},
    {"user_name": "Desire Ndayisaba",         "email": "driver15@demo.rw", "user_phone_no": "250788100015", "password": "demo1234", "licence_no": "RW-DL-110015", "latitude": -1.9580, "longitude": 30.0680, "rating": 4.2, "plate_no": "RAO 015 O", "capacity": 3.0},
    {"user_name": "Julienne Mukashyaka",      "email": "driver16@demo.rw", "user_phone_no": "250788100016", "password": "demo1234", "licence_no": "RW-DL-110016", "latitude": -1.9180, "longitude": 30.0820, "rating": 4.7, "plate_no": "RAP 016 P", "capacity": 4.5},
    {"user_name": "Olivier Nsengimana",       "email": "driver17@demo.rw", "user_phone_no": "250788100017", "password": "demo1234", "licence_no": "RW-DL-110017", "latitude": -1.9620, "longitude": 30.0530, "rating": 3.7, "plate_no": "RAQ 017 Q", "capacity": 8.0},
    {"user_name": "Francine Umurerwa",        "email": "driver18@demo.rw", "user_phone_no": "250788100018", "password": "demo1234", "licence_no": "RW-DL-110018", "latitude": -1.9330, "longitude": 30.0870, "rating": 4.6, "plate_no": "RAR 018 R", "capacity": 2.0},
    {"user_name": "Celestin Muhire",          "email": "driver19@demo.rw", "user_phone_no": "250788100019", "password": "demo1234", "licence_no": "RW-DL-110019", "latitude": -1.9480, "longitude": 30.0420, "rating": 4.1, "plate_no": "RAS 019 S", "capacity": 6.0},
    {"user_name": "Annonciata Nyiransabimana","email": "driver20@demo.rw", "user_phone_no": "250788100020", "password": "demo1234", "licence_no": "RW-DL-110020", "latitude": -1.9050, "longitude": 30.0600, "rating": 4.8, "plate_no": "RAT 020 T", "capacity": 3.0},
    {"user_name": "Modeste Bizumuremyi",      "email": "driver21@demo.rw", "user_phone_no": "250788100021", "password": "demo1234", "licence_no": "RW-DL-110021", "latitude": -1.9730, "longitude": 30.0710, "rating": 4.3, "plate_no": "RAU 021 U", "capacity": 1.5},
    {"user_name": "Speciose Uwimana",         "email": "driver22@demo.rw", "user_phone_no": "250788100022", "password": "demo1234", "licence_no": "RW-DL-110022", "latitude": -1.9220, "longitude": 30.0490, "rating": 4.5, "plate_no": "RAV 022 V", "capacity": 9.0},
    {"user_name": "Augustin Kayitare",        "email": "driver23@demo.rw", "user_phone_no": "250788100023", "password": "demo1234", "licence_no": "RW-DL-110023", "latitude": -1.9460, "longitude": 30.0780, "rating": 4.0, "plate_no": "RAW 023 W", "capacity": 4.0},
    {"user_name": "Esperance Uwamariya",      "email": "driver24@demo.rw", "user_phone_no": "250788100024", "password": "demo1234", "licence_no": "RW-DL-110024", "latitude": -1.9680, "longitude": 30.0590, "rating": 4.4, "plate_no": "RAX 024 X", "capacity": 2.5},
    {"user_name": "Gedeon Ntirandekura",      "email": "driver25@demo.rw", "user_phone_no": "250788100025", "password": "demo1234", "licence_no": "RW-DL-110025", "latitude": -1.9120, "longitude": 30.0850, "rating": 3.9, "plate_no": "RAY 025 Y", "capacity": 5.0},
]

# ─────────────────────────────────────────────
#  Ola's booking history data
# ─────────────────────────────────────────────
KIGALI_PICKUPS = [
    "KG 7 Ave, Kacyiru, Kigali",
    "KN 3 Rd, Nyarugenge, Kigali",
    "KG 11 Ave, Kimihurura, Kigali",
    "KN 78 St, Remera, Kigali",
    "KG 200 St, Gisozi, Kigali",
    "KN 5 Rd, Gikondo, Kigali",
    "KG 14 Ave, Kicukiro, Kigali",
    "KN 22 St, Kagarama, Kigali",
]

KIGALI_DROPOFFS = [
    "KG 9 Ave, Kibagabaga, Kigali",
    "KN 13 Rd, Kimironko, Kigali",
    "KG 30 Ave, Kanombe, Kigali",
    "KN 4 St, Nyamirambo, Kigali",
    "KG 15 Ave, Masaka, Kigali",
    "KN 44 St, Gahanga, Kigali",
    "KG 82 St, Nyacyonga, Kigali",
    "KN 56 Ave, Biryogo, Kigali",
]

CUSTOMER_NAMES = [
    ("Alice Uwase",     "alice.uwase@email.rw",   "+250788100001"),
    ("Bruno Nshuti",    "bruno.nshuti@email.rw",  "+250788100002"),
    ("Clarisse Mukamana","clarisse.m@email.rw",   "+250788100003"),
    ("David Habimana",  "david.h@email.rw",       "+250788100004"),
]

RATINGS_COMMENTS = [
    "Great driver, very professional!",
    "On time and careful with my cargo.",
    "Good service.",
    "Would use again.",
    None,
]


def seed_drivers():
    """Create 25 verified demo drivers across Kigali."""
    print("=== Seeding 25 demo drivers ===\n")
    created = 0
    skipped = 0
    for data in DEMO_DRIVERS:
        if User.query.filter_by(email=data["email"]).first():
            print(f"  [SKIP] {data['email']} already exists.")
            skipped += 1
            continue

        # Create user account
        user = User(
            user_name=data["user_name"],
            email=data["email"],
            user_phone_no=data["user_phone_no"],
            password_hash=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
            role="driver",
        )
        db.session.add(user)
        db.session.flush()

        # Create driver profile
        driver = Driver(
            user_id=user.user_id,
            licence_no=data["licence_no"],
            rating=data["rating"],
            is_available=True,
            is_verified=True,
            latitude=data["latitude"],
            longitude=data["longitude"],
        )
        db.session.add(driver)
        db.session.flush()

        # Assign truck
        truck = Truck(
            driver_id=driver.driver_id,
            plate_no=data["plate_no"],
            capacity=data["capacity"],
        )
        db.session.add(truck)
        created += 1
        print(f"  [ADD]  {data['user_name']} — {data['plate_no']} ({data['capacity']} t)")

    db.session.commit()
    print(f"\nDone. {created} driver(s) created, {skipped} skipped.")


def seed_ola():
    """Create driver Ola with 12 weeks of completed bookings, payments, and ratings."""
    print("\n=== Seeding data for driver Ola ===\n")

    pw_hash = bcrypt.generate_password_hash("password123").decode("utf-8")

    # Create or fetch Ola's user account
    ola_user = User.query.filter_by(email="ola.ndayisaba@cargoconnect.rw").first()
    if not ola_user:
        ola_user = User(
            user_name="Ola Ndayisaba",
            email="ola.ndayisaba@cargoconnect.rw",
            user_phone_no="+250788200001",
            role="driver",
            password_hash=pw_hash,
        )
        db.session.add(ola_user)
        db.session.flush()
        print("  Created user: Ola Ndayisaba (driver)")
    else:
        print("  Found existing user: Ola Ndayisaba")

    # Create or fetch driver profile
    driver = Driver.query.filter_by(user_id=ola_user.user_id).first()
    if not driver:
        driver = Driver(
            user_id=ola_user.user_id,
            licence_no="RW-DL-2021-0042",
            rating=4.3,
            is_available=True,
            is_verified=True,
            latitude=-1.9441,
            longitude=30.0619,
        )
        db.session.add(driver)
        db.session.flush()
        print("  Created driver profile for Ola")
    else:
        driver.is_verified = True
        driver.is_available = True
        print("  Found existing driver profile for Ola")

    # Create or fetch truck
    if not driver.trucks:
        truck = Truck(
            driver_id=driver.driver_id,
            plate_no="RAC 042 B",
            capacity=5.0,
        )
        db.session.add(truck)
        db.session.flush()
        print("  Created truck: RAC 042 B (5 tons)")
    else:
        truck = driver.trucks[0]
        print(f"  Found existing truck: {truck.plate_no}")

    # Create or fetch customers
    customers = []
    for name, email, phone in CUSTOMER_NAMES:
        c_user = User.query.filter_by(email=email).first()
        if not c_user:
            c_user = User(
                user_name=name,
                email=email,
                user_phone_no=phone,
                role="customer",
                password_hash=pw_hash,
            )
            db.session.add(c_user)
            db.session.flush()
            print(f"  Created user: {name} (customer)")
        else:
            print(f"  Found existing user: {name}")

        c_profile = Customer.query.filter_by(user_id=c_user.user_id).first()
        if not c_profile:
            c_profile = Customer(user_id=c_user.user_id, default_address="Kigali, Rwanda")
            db.session.add(c_profile)
            db.session.flush()
        customers.append(c_profile)

    db.session.commit()

    # Create completed bookings spread over 12 weeks
    print("\n  Creating completed bookings over the last 12 weeks...")
    now = datetime.utcnow()
    weekly_jobs = [5, 3, 6, 4, 7, 2, 5, 4, 6, 3, 5, 4]
    cost_range = (15000, 85000)
    created_bookings = 0

    for week_idx, num_jobs in enumerate(weekly_jobs):
        week_start = now - timedelta(weeks=12 - week_idx)
        for _ in range(num_jobs):
            job_time = week_start + timedelta(
                days=random.randint(0, 6),
                hours=random.randint(7, 18)
            )
            customer = random.choice(customers)
            cost = Decimal(str(random.randint(*cost_range) // 500 * 500))
            weight = round(random.uniform(0.5, 4.5), 1)

            booking = Booking(
                customer_id=customer.customer_id,
                truck_id=truck.truck_id,
                driver_id=driver.driver_id,
                pickup_address=random.choice(KIGALI_PICKUPS),
                dropoff_address=random.choice(KIGALI_DROPOFFS),
                scheduled_time=job_time,
                cargo_weight=weight,
                estimated_cost=cost,
                status="completed",
                created_at=job_time,
            )
            db.session.add(booking)
            db.session.flush()

            # Payment
            payment = Payment(
                booking_id=booking.booking_id,
                amount=cost,
                method="MoMo",
                status="paid",
                paid_at=job_time + timedelta(minutes=random.randint(5, 60)),
            )
            db.session.add(payment)

            # Rating — 80% of jobs get rated
            if random.random() < 0.8:
                rating = Rating(
                    booking_id=booking.booking_id,
                    customer_id=customer.customer_id,
                    driver_id=driver.driver_id,
                    rating_score=round(random.choice([3.5, 4.0, 4.0, 4.5, 4.5, 5.0]), 1),
                    comment=random.choice(RATINGS_COMMENTS),
                    created_at=job_time + timedelta(hours=random.randint(1, 5)),
                )
                db.session.add(rating)

            created_bookings += 1

    db.session.commit()

    # Recompute Ola's average rating
    all_ratings = Rating.query.filter_by(driver_id=driver.driver_id).all()
    if all_ratings:
        driver.rating = round(sum(r.rating_score for r in all_ratings) / len(all_ratings), 2)
        db.session.commit()

    total_earnings = sum(
        float(b.estimated_cost)
        for b in Booking.query.filter_by(driver_id=driver.driver_id, status="completed").all()
    )

    print(f"\n=== Ola seed complete ===")
    print(f"  Bookings created : {created_bookings}")
    print(f"  Total earnings   : {total_earnings:,.0f} RWF")
    print(f"  Avg rating       : {driver.rating}")
    print(f"  Login            : ola.ndayisaba@cargoconnect.rw / password123")


if __name__ == "__main__":
    with app.app_context():
        seed_drivers()
        seed_ola()
