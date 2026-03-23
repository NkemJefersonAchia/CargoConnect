from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.driver import Driver
from models.booking import Booking
from models.payment import Payment
from models.rating import Rating
from models.notification import Notification
from models.customer import Customer

driver_bp = Blueprint("driver", __name__)


def success(data, message="OK"):
    """Return a standard success JSON response."""
    return jsonify({"status": "success", "data": data, "message": message})


def error(message, code=400):
    """Return a standard error JSON response."""
    return jsonify({"status": "error", "data": None, "message": message}), code


def require_driver(f):
    """Decorator that restricts access to drivers only."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "driver":
            return error("Access denied.", 403)
        return f(*args, **kwargs)
    return decorated


@driver_bp.route("/dashboard")
@login_required
@require_driver
def dashboard():
    """Render the driver dashboard page."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    return render_template("driver-home.html", driver=driver, user=current_user)


@driver_bp.route("/stats", methods=["GET"])
@login_required
@require_driver
def stats():
    """Return driver statistics for the dashboard."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()

    total_jobs = Booking.query.filter_by(driver_id=driver.driver_id, status="completed").count()

    one_week_ago = datetime.utcnow() - timedelta(days=7)
    week_bookings = Booking.query.filter(
        Booking.driver_id == driver.driver_id,
        Booking.status == "completed",
        Booking.created_at >= one_week_ago,
    ).all()
    weekly_earnings = sum(float(b.estimated_cost or 0) for b in week_bookings)

    pending_jobs = Booking.query.filter_by(driver_id=driver.driver_id, status="pending").count()

    return success({
        "total_jobs": total_jobs,
        "average_rating": round(driver.rating, 1),
        "weekly_earnings": round(weekly_earnings, 2),
        "pending_jobs": pending_jobs,
    })


@driver_bp.route("/availability", methods=["PATCH"])
@login_required
@require_driver
def toggle_availability():
    """Toggle the driver's online/offline availability status."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    if not driver.is_verified:
        return error("Account pending verification.", 403)

    data = request.get_json() or {}
    driver.is_available = bool(data.get("is_available", not driver.is_available))
    db.session.commit()
    return success({"is_available": driver.is_available}, "Availability updated.")


@driver_bp.route("/pending-jobs", methods=["GET"])
@login_required
@require_driver
def pending_jobs():
    """Return pending bookings assigned to this driver."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    bookings = Booking.query.filter_by(driver_id=driver.driver_id, status="pending").all()
    return success([_serialize_booking(b) for b in bookings])


@driver_bp.route("/active-job", methods=["GET"])
@login_required
@require_driver
def active_job():
    """Return the driver's currently confirmed booking if any."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.filter_by(driver_id=driver.driver_id, status="confirmed").first()
    if not booking:
        return success(None, "No active job.")
    return success(_serialize_booking(booking))


@driver_bp.route("/job/<int:booking_id>/accept", methods=["POST"])
@login_required
@require_driver
def accept_job(booking_id):
    """Accept a pending booking and set it to confirmed."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.filter_by(booking_id=booking_id, driver_id=driver.driver_id).first_or_404()

    if booking.status != "pending":
        return error("Booking is not pending.")

    booking.status = "confirmed"
    note = Notification(
        user_id=booking.customer.user_id,
        message=f"Your booking #{booking_id} has been confirmed by {current_user.user_name}.",
        channel="in-app",
    )
    db.session.add(note)
    db.session.commit()
    return success(None, "Job accepted.")


@driver_bp.route("/job/<int:booking_id>/decline", methods=["POST"])
@login_required
@require_driver
def decline_job(booking_id):
    """Decline a pending booking."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.filter_by(booking_id=booking_id, driver_id=driver.driver_id).first_or_404()

    if booking.status != "pending":
        return error("Booking is not pending.")

    booking.status = "cancelled"
    db.session.commit()
    return success(None, "Job declined.")


@driver_bp.route("/job/<int:booking_id>/complete", methods=["POST"])
@login_required
@require_driver
def complete_job(booking_id):
    """Mark a confirmed booking as completed and create payment record."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.filter_by(booking_id=booking_id, driver_id=driver.driver_id).first_or_404()

    if booking.status != "confirmed":
        return error("Only confirmed jobs can be completed.")

    booking.status = "completed"

    if not booking.payment:
        payment = Payment(
            booking_id=booking_id,
            amount=booking.estimated_cost or 0,
            status="pending",
        )
        db.session.add(payment)

    note_customer = Notification(
        user_id=booking.customer.user_id,
        message=f"Trip #{booking_id} completed. Please rate your driver.",
        channel="in-app",
    )
    note_driver = Notification(
        user_id=driver.user_id,
        message=f"Trip #{booking_id} marked as completed.",
        channel="in-app",
    )
    db.session.add(note_customer)
    db.session.add(note_driver)
    db.session.commit()
    return success(None, "Trip completed.")


@driver_bp.route("/job-history", methods=["GET"])
@login_required
@require_driver
def job_history():
    """Return the driver's ten most recent completed jobs."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    bookings = (
        Booking.query.filter_by(driver_id=driver.driver_id, status="completed")
        .order_by(Booking.created_at.desc())
        .limit(10)
        .all()
    )
    return success([_serialize_booking_history(b) for b in bookings])


@driver_bp.route("/job/<int:booking_id>")
@login_required
@require_driver
def driver_job_page(booking_id):
    """Render the active job detail page."""
    driver = Driver.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.get_or_404(booking_id)
    return render_template("driver-job-history.html", booking=booking, driver=driver, user=current_user)


def _serialize_booking(b):
    """Serialize a booking for driver views."""
    customer_phone = b.customer.user.user_phone_no if b.customer else ""
    return {
        "booking_id": b.booking_id,
        "customer_name": b.customer.user.user_name if b.customer else "",
        "customer_phone": customer_phone,
        "pickup_address": b.pickup_address,
        "dropoff_address": b.dropoff_address,
        "estimated_cost": float(b.estimated_cost or 0),
        "scheduled_time": b.scheduled_time.isoformat() if b.scheduled_time else None,
        "status": b.status,
    }


def _serialize_booking_history(b):
    """Serialize a completed booking for the job history table."""
    rating = Rating.query.filter_by(booking_id=b.booking_id, driver_id=b.driver_id).first()
    return {
        "booking_id": b.booking_id,
        "customer_name": b.customer.user.user_name if b.customer else "",
        "date": b.created_at.strftime("%Y-%m-%d") if b.created_at else "",
        "earnings": float(b.estimated_cost or 0),
        "rating": rating.rating_score if rating else None,
    }
