from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from extensions import socketio
from flask_socketio import join_room, emit
from models import db
from models.driver import Driver
from models.booking import Booking

tracking_bp = Blueprint("tracking", __name__)


@tracking_bp.route("/track/<int:booking_id>")
@login_required
def track_booking(booking_id):
    """Render the live tracking map for a specific booking."""
    booking = Booking.query.get_or_404(booking_id)

    # Only the customer who owns this booking, the assigned driver, or an admin may view it
    is_customer = (
        current_user.role == "customer"
        and booking.customer
        and booking.customer.user_id == current_user.user_id
    )
    is_driver = (
        current_user.role == "driver"
        and booking.driver
        and booking.driver.user_id == current_user.user_id
    )
    is_admin = current_user.role == "admin"

    if not (is_customer or is_driver or is_admin):
        abort(403)

    return render_template("track_booking.html", booking=booking, user=current_user)


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
