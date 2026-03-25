import math
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.customer import Customer
from models.driver import Driver
from models.truck import Truck
from models.notification import Notification

booking_bp = Blueprint("booking", __name__)

KIGALI_LAT = -1.9441
KIGALI_LNG = 30.0619
BASE_FARE = 2000
COST_PER_TON = 500
COST_PER_KM = 200


def success(data, message="OK"):
    """Return a standard success JSON response."""
    return jsonify({"status": "success", "data": data, "message": message})


def error(message, code=400):
    """Return a standard error JSON response."""
    return jsonify({"status": "error", "data": None, "message": message}), code


def haversine(lat1, lng1, lat2, lng2):
    """Compute great-circle distance in km between two points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def estimate_cost(weight_tons, distance_km):
    """Calculate estimated trip cost in RWF."""
    return BASE_FARE + (COST_PER_TON * weight_tons) + (COST_PER_KM * distance_km)


def find_available_drivers(pickup_lat, pickup_lng, required_capacity):
    """Find verified, available drivers near a pickup location with enough capacity."""
    confirmed_driver_ids = db.session.query(Booking.driver_id).filter(
        Booking.status == "confirmed"
    ).subquery()

    drivers = (
        Driver.query.filter(
            Driver.is_verified == True,
            Driver.is_available == True,
            Driver.driver_id.notin_(confirmed_driver_ids),
        )
        .join(Truck, Driver.driver_id == Truck.driver_id)
        .filter(Truck.capacity >= required_capacity)
        .all()
    )

    results = []
    no_coords = []
    for driver in drivers:
        truck = Truck.query.filter(
            Truck.driver_id == driver.driver_id,
            Truck.capacity >= required_capacity,
        ).first()
        if not truck:
            continue

        if driver.latitude and driver.longitude:
            dist = haversine(pickup_lat, pickup_lng, driver.latitude, driver.longitude)
            cost = estimate_cost(required_capacity, dist)
            results.append({"driver": driver, "truck": truck, "distance_km": round(dist, 2), "cost": round(cost, 2)})
        else:
            cost = estimate_cost(required_capacity, 5)
            no_coords.append({"driver": driver, "truck": truck, "distance_km": None, "cost": round(cost, 2)})

    results.sort(key=lambda x: x["driver"].rating, reverse=True)
    return (results + no_coords)[:10]


def serialize_driver_result(item):
    """Serialize a driver search result to a dict."""
    driver = item["driver"]
    truck = item["truck"]
    return {
        "driver_id": driver.driver_id,
        "driver_name": driver.user.user_name,
        "rating": driver.rating,
        "truck_id": truck.truck_id,
        "plate_no": truck.plate_no,
        "capacity": truck.capacity,
        "distance_km": item["distance_km"],
        "estimated_cost": item["cost"],
    }


@booking_bp.route("/search", methods=["POST"])
@login_required
def search_trucks():
    """Search for available drivers matching cargo requirements."""
    data = request.get_json() or request.form
    try:
        weight = float(data.get("weight", 0))
        pickup_lat = float(data.get("pickup_lat", KIGALI_LAT))
        pickup_lng = float(data.get("pickup_lng", KIGALI_LNG))
    except (ValueError, TypeError):
        return error("Invalid input values.")

    drivers = find_available_drivers(pickup_lat, pickup_lng, weight)
    return success([serialize_driver_result(d) for d in drivers], f"Found {len(drivers)} driver(s)")


@booking_bp.route("/create", methods=["POST"])
@login_required
def create_booking():
    """Create a new booking for the current customer."""
    if current_user.role != "customer":
        return error("Only customers can create bookings.", 403)

    # Parse and validate request body first (no DB needed)
    data = request.get_json() or request.form
    try:
        truck_id = int(data.get("truck_id"))
        driver_id = int(data.get("driver_id"))
        pickup_address = data.get("pickup_address", "").strip()
        dropoff_address = data.get("dropoff_address", "").strip()
        scheduled_time = datetime.fromisoformat(data.get("scheduled_time"))
        cargo_weight = float(data.get("cargo_weight") or 1.0)
        estimated_cost = float(data.get("estimated_cost", 0))
    except (ValueError, TypeError, KeyError) as e:
        return error(f"Invalid booking data: {e}")

    if not pickup_address or not dropoff_address:
        return error("Pickup and dropoff addresses are required.")

    # All DB work in one try/except so any connection hiccup returns JSON
    try:
        customer = Customer.query.filter_by(user_id=current_user.user_id).first()
        if not customer:
            return error("Customer profile not found.", 404)

        booking = Booking(
            customer_id=customer.customer_id,
            truck_id=truck_id,
            driver_id=driver_id,
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            scheduled_time=scheduled_time,
            cargo_weight=cargo_weight,
            estimated_cost=estimated_cost,
            status="pending",
        )
        db.session.add(booking)

        driver = Driver.query.get(driver_id)
        if driver:
            note = Notification(
                user_id=driver.user_id,
                message=f"New booking request from {current_user.user_name}. Pickup: {pickup_address}",
                channel="in-app",
            )
            db.session.add(note)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"Failed to save booking: {e}", 500)

    return success({"booking_id": booking.booking_id}, "Booking created successfully.")


@booking_bp.route("/<int:booking_id>", methods=["GET"])
@login_required
def get_booking(booking_id):
    """Fetch details for a single booking."""
    booking = Booking.query.get_or_404(booking_id)
    return success(_serialize_booking(booking), "Booking details.")


@booking_bp.route("/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    """Cancel a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.status not in ("pending",):
        return error("Only pending bookings can be cancelled.")
    booking.status = "cancelled"
    db.session.commit()
    return success(None, "Booking cancelled.")


def _serialize_booking(b):
    """Convert a Booking object to a serializable dict."""
    return {
        "booking_id": b.booking_id,
        "pickup_address": b.pickup_address,
        "dropoff_address": b.dropoff_address,
        "scheduled_time": b.scheduled_time.isoformat() if b.scheduled_time else None,
        "estimated_cost": float(b.estimated_cost) if b.estimated_cost else 0,
        "status": b.status,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "driver_name": b.driver.user.user_name if b.driver and b.driver.user else None,
        "plate_no": b.truck.plate_no if b.truck else None,
        "customer_name": b.customer.user.user_name if b.customer else None,
    }
