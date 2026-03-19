"""
seed.py — populate the database with 5 demo drivers and trucks.
Run once from the project root:

    python seed.py

Safe to re-run: skips any driver whose email already exists.
"""
import eventlet
eventlet.monkey_patch()

# Import the already-created app instance (avoids double-initialisation)
from app import app
from extensions import db, bcrypt
from models.user import User
from models.driver import Driver
from models.truck import Truck

DEMO_DRIVERS = [
    {
        "user_name": "Jean Paul Habimana",
        "email": "driver1@demo.rw",
        "user_phone_no": "250788100001",
        "password": "demo1234",
        "licence_no": "RW-DL-110001",
        "latitude": -1.9500,
        "longitude": 30.0580,
        "rating": 4.8,
        "plate_no": "RAA 001 A",
        "capacity": 3.0,
    },
    {
        "user_name": "Marie Claire Uwase",
        "email": "driver2@demo.rw",
        "user_phone_no": "250788100002",
        "password": "demo1234",
        "licence_no": "RW-DL-110002",
        "latitude": -1.9350,
        "longitude": 30.0700,
        "rating": 4.5,
        "plate_no": "RAB 002 B",
        "capacity": 5.0,
    },
    {
        "user_name": "Emmanuel Nzeyimana",
        "email": "driver3@demo.rw",
        "user_phone_no": "250788100003",
        "password": "demo1234",
        "licence_no": "RW-DL-110003",
        "latitude": -1.9600,
        "longitude": 30.0500,
        "rating": 4.2,
        "plate_no": "RAC 003 C",
        "capacity": 2.0,
    },
    {
        "user_name": "Aline Mukamana",
        "email": "driver4@demo.rw",
        "user_phone_no": "250788100004",
        "password": "demo1234",
        "licence_no": "RW-DL-110004",
        "latitude": -1.9200,
        "longitude": 30.0800,
        "rating": 4.9,
        "plate_no": "RAD 004 D",
        "capacity": 8.0,
    },
    {
        "user_name": "Patrick Bizimana",
        "email": "driver5@demo.rw",
        "user_phone_no": "250788100005",
        "password": "demo1234",
        "licence_no": "RW-DL-110005",
        "latitude": -1.9441,
        "longitude": 30.0619,
        "rating": 3.9,
        "plate_no": "RAE 005 E",
        "capacity": 1.5,
    },
    {
        "user_name": "Claudine Umubyeyi",
        "email": "driver6@demo.rw",
        "user_phone_no": "250788100006",
        "password": "demo1234",
        "licence_no": "RW-DL-110006",
        "latitude": -1.9300,
        "longitude": 30.0550,
        "rating": 4.7,
        "plate_no": "RAF 006 F",
        "capacity": 4.0,
    },
    {
        "user_name": "Innocent Nshimiyimana",
        "email": "driver7@demo.rw",
        "user_phone_no": "250788100007",
        "password": "demo1234",
        "licence_no": "RW-DL-110007",
        "latitude": -1.9550,
        "longitude": 30.0750,
        "rating": 4.1,
        "plate_no": "RAG 007 G",
        "capacity": 6.0,
    },
    {
        "user_name": "Vestine Ingabire",
        "email": "driver8@demo.rw",
        "user_phone_no": "250788100008",
        "password": "demo1234",
        "licence_no": "RW-DL-110008",
        "latitude": -1.9150,
        "longitude": 30.0650,
        "rating": 4.6,
        "plate_no": "RAH 008 H",
        "capacity": 2.5,
    },
    {
        "user_name": "Faustin Nkurunziza",
        "email": "driver9@demo.rw",
        "user_phone_no": "250788100009",
        "password": "demo1234",
        "licence_no": "RW-DL-110009",
        "latitude": -1.9650,
        "longitude": 30.0450,
        "rating": 3.8,
        "plate_no": "RAI 009 I",
        "capacity": 10.0,
    },
    {
        "user_name": "Solange Mutesi",
        "email": "driver10@demo.rw",
        "user_phone_no": "250788100010",
        "password": "demo1234",
        "licence_no": "RW-DL-110010",
        "latitude": -1.9400,
        "longitude": 30.0900,
        "rating": 4.4,
        "plate_no": "RAJ 010 J",
        "capacity": 3.5,
    },
    {
        "user_name": "Theogene Hakizimana",
        "email": "driver11@demo.rw",
        "user_phone_no": "250788100011",
        "password": "demo1234",
        "licence_no": "RW-DL-110011",
        "latitude": -1.9250,
        "longitude": 30.0480,
        "rating": 4.3,
        "plate_no": "RAK 011 K",
        "capacity": 1.5,
    },
    {
        "user_name": "Beatrice Uwineza",
        "email": "driver12@demo.rw",
        "user_phone_no": "250788100012",
        "password": "demo1234",
        "licence_no": "RW-DL-110012",
        "latitude": -1.9700,
        "longitude": 30.0620,
        "rating": 4.9,
        "plate_no": "RAL 012 L",
        "capacity": 7.0,
    },
    {
        "user_name": "Alexis Munyaneza",
        "email": "driver13@demo.rw",
        "user_phone_no": "250788100013",
        "password": "demo1234",
        "licence_no": "RW-DL-110013",
        "latitude": -1.9100,
        "longitude": 30.0730,
        "rating": 4.0,
        "plate_no": "RAM 013 M",
        "capacity": 2.0,
    },
    {
        "user_name": "Clarisse Nyirahabimana",
        "email": "driver14@demo.rw",
        "user_phone_no": "250788100014",
        "password": "demo1234",
        "licence_no": "RW-DL-110014",
        "latitude": -1.9380,
        "longitude": 30.0560,
        "rating": 4.5,
        "plate_no": "RAN 014 N",
        "capacity": 5.0,
    },
    {
        "user_name": "Desire Ndayisaba",
        "email": "driver15@demo.rw",
        "user_phone_no": "250788100015",
        "password": "demo1234",
        "licence_no": "RW-DL-110015",
        "latitude": -1.9580,
        "longitude": 30.0680,
        "rating": 4.2,
        "plate_no": "RAO 015 O",
        "capacity": 3.0,
    },
    {
        "user_name": "Julienne Mukashyaka",
        "email": "driver16@demo.rw",
        "user_phone_no": "250788100016",
        "password": "demo1234",
        "licence_no": "RW-DL-110016",
        "latitude": -1.9180,
        "longitude": 30.0820,
        "rating": 4.7,
        "plate_no": "RAP 016 P",
        "capacity": 4.5,
    },
    {
        "user_name": "Olivier Nsengimana",
        "email": "driver17@demo.rw",
        "user_phone_no": "250788100017",
        "password": "demo1234",
        "licence_no": "RW-DL-110017",
        "latitude": -1.9620,
        "longitude": 30.0530,
        "rating": 3.7,
        "plate_no": "RAQ 017 Q",
        "capacity": 8.0,
    },
    {
        "user_name": "Francine Umurerwa",
        "email": "driver18@demo.rw",
        "user_phone_no": "250788100018",
        "password": "demo1234",
        "licence_no": "RW-DL-110018",
        "latitude": -1.9330,
        "longitude": 30.0870,
        "rating": 4.6,
        "plate_no": "RAR 018 R",
        "capacity": 2.0,
    },
    {
        "user_name": "Celestin Muhire",
        "email": "driver19@demo.rw",
        "user_phone_no": "250788100019",
        "password": "demo1234",
        "licence_no": "RW-DL-110019",
        "latitude": -1.9480,
        "longitude": 30.0420,
        "rating": 4.1,
        "plate_no": "RAS 019 S",
        "capacity": 6.0,
    },
    {
        "user_name": "Annonciata Nyiransabimana",
        "email": "driver20@demo.rw",
        "user_phone_no": "250788100020",
        "password": "demo1234",
        "licence_no": "RW-DL-110020",
        "latitude": -1.9050,
        "longitude": 30.0600,
        "rating": 4.8,
        "plate_no": "RAT 020 T",
        "capacity": 3.0,
    },
    {
        "user_name": "Modeste Bizumuremyi",
        "email": "driver21@demo.rw",
        "user_phone_no": "250788100021",
        "password": "demo1234",
        "licence_no": "RW-DL-110021",
        "latitude": -1.9730,
        "longitude": 30.0710,
        "rating": 4.3,
        "plate_no": "RAU 021 U",
        "capacity": 1.5,
    },
    {
        "user_name": "Speciose Uwimana",
        "email": "driver22@demo.rw",
        "user_phone_no": "250788100022",
        "password": "demo1234",
        "licence_no": "RW-DL-110022",
        "latitude": -1.9220,
        "longitude": 30.0490,
        "rating": 4.5,
        "plate_no": "RAV 022 V",
        "capacity": 9.0,
    },
    {
        "user_name": "Augustin Kayitare",
        "email": "driver23@demo.rw",
        "user_phone_no": "250788100023",
        "password": "demo1234",
        "licence_no": "RW-DL-110023",
        "latitude": -1.9460,
        "longitude": 30.0780,
        "rating": 4.0,
        "plate_no": "RAW 023 W",
        "capacity": 4.0,
    },
    {
        "user_name": "Esperance Uwamariya",
        "email": "driver24@demo.rw",
        "user_phone_no": "250788100024",
        "password": "demo1234",
        "licence_no": "RW-DL-110024",
        "latitude": -1.9680,
        "longitude": 30.0590,
        "rating": 4.4,
        "plate_no": "RAX 024 X",
        "capacity": 2.5,
    },
    {
        "user_name": "Gedeon Ntirandekura",
        "email": "driver25@demo.rw",
        "user_phone_no": "250788100025",
        "password": "demo1234",
        "licence_no": "RW-DL-110025",
        "latitude": -1.9120,
        "longitude": 30.0850,
        "rating": 3.9,
        "plate_no": "RAY 025 Y",
        "capacity": 5.0,
    },
]


def seed():
    with app.app_context():
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
            db.session.flush()  # get user_id before commit

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
            db.session.flush()  # get driver_id before truck

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


if __name__ == "__main__":
    seed()
