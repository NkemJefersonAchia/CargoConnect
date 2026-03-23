# Tracking module — handles live GPS tracking and real-time location updates
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from extensions import socketio
from flask_socketio import join_room, emit
from models import db
from models.driver import Driver
from models.booking import Booking
from models.customer import Customer

tracking_bp = Blueprint("tracking", __name__)


# ── Route: render the live tracking page for a given booking ──
@tracking_bp.route("/track/<int:booking_id>")
@login_required
def track_booking(booking_id):
    """Render the live tracking map for a booking."""
    booking = Booking.query.get_or_404(booking_id)
    return render_template("track.html", booking=booking, user=current_user)


@socketio.on("join_tracking_room")
def handle_join_room(data):
    """Customer joins the SocketIO room for their booking."""
    booking_id = data.get("booking_id")
    if booking_id:
        join_room(str(booking_id))
        emit("joined", {"room": str(booking_id)})


@socketio.on("driver_location_update")
def handle_driver_location(data):
    """Receive GPS update from driver and broadcast to booking room."""
    driver_id = data.get("driver_id")
    booking_id = data.get("booking_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not all([driver_id, booking_id, latitude, longitude]):
        return

    driver = Driver.query.get(driver_id)
    if driver:
        driver.latitude = latitude
        driver.longitude = longitude
        db.session.commit()

    emit(
        "location_update",
        {"driver_id": driver_id, "latitude": latitude, "longitude": longitude},
        room=str(booking_id),
    )
