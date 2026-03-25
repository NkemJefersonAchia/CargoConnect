from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.customer import Customer
from models.booking import Booking
from models.notification import Notification
from models.rating import Rating
from models.driver import Driver

customer_bp = Blueprint("customer", __name__)


def success(data, message="OK"):
    """Return a standard success JSON response."""
    return jsonify({"status": "success", "data": data, "message": message})


def error(message, code=400):
    """Return a standard error JSON response."""
    return jsonify({"status": "error", "data": None, "message": message}), code


def require_customer(f):
    """Decorator that restricts access to customers only."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != "customer":
            return error("Access denied.", 403)
        return f(*args, **kwargs)
    return decorated


@customer_bp.route("/dashboard")
@login_required
@require_customer
def dashboard():
    """Render the customer dashboard page."""
    customer = Customer.query.filter_by(user_id=current_user.user_id).first_or_404()
    return render_template("customer_dashboard.html", customer=customer, user=current_user)


@customer_bp.route("/stats", methods=["GET"])
@login_required
@require_customer
def stats():
    """Return dashboard stats for the current customer."""
    try:
        customer = Customer.query.filter_by(user_id=current_user.user_id).first_or_404()
        total = Booking.query.filter_by(customer_id=customer.customer_id).count()
        completed = Booking.query.filter_by(customer_id=customer.customer_id, status="completed").count()
        pending = Booking.query.filter_by(customer_id=customer.customer_id, status="pending").count()
        spent = db.session.query(db.func.sum(Booking.estimated_cost)).filter(
            Booking.customer_id == customer.customer_id,
            Booking.status == "completed",
        ).scalar() or 0
        return success({
            "total_bookings": total,
            "completed_trips": completed,
            "pending_bookings": pending,
            "total_spent": float(spent),
        })
    except Exception as e:
        return error(f"Could not load stats: {e}", 500)


@customer_bp.route("/active-booking", methods=["GET"])
@login_required
@require_customer
def active_booking():
    """Return the customer's current confirmed booking if any."""
    try:
        customer = Customer.query.filter_by(user_id=current_user.user_id).first_or_404()
        booking = Booking.query.filter_by(
            customer_id=customer.customer_id, status="confirmed"
        ).first()
        if not booking:
            return success(None, "No active booking.")
        return success(_serialize_booking(booking))
    except Exception as e:
        return error(f"Could not load active booking: {e}", 500)


@customer_bp.route("/recent-bookings", methods=["GET"])
@login_required
@require_customer
def recent_bookings():
    """Return the customer's five most recent bookings."""
    try:
        customer = Customer.query.filter_by(user_id=current_user.user_id).first_or_404()
        bookings = (
            Booking.query
            .filter_by(customer_id=customer.customer_id)
            .order_by(Booking.created_at.desc())
            .limit(5)
            .all()
        )
        return success([_serialize_booking(b) for b in bookings])
    except Exception as e:
        return error(f"Could not load bookings: {e}", 500)


@customer_bp.route("/notifications", methods=["GET"])
@login_required
def notifications():
    """Return unread notification count and list."""
    notes = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).all()
    return success({
        "count": len(notes),
        "items": [{"id": n.notification_id, "message": n.message, "sent_at": n.sent_at.isoformat()} for n in notes],
    })


@customer_bp.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    """Mark all notifications as read for the current user."""
    Notification.query.filter_by(user_id=current_user.user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return success(None, "Marked as read.")


@customer_bp.route("/rate/<int:booking_id>", methods=["POST"])
@login_required
@require_customer
def rate_driver(booking_id):
    """Submit a rating for a completed booking."""
    customer = Customer.query.filter_by(user_id=current_user.user_id).first_or_404()
    booking = Booking.query.filter_by(booking_id=booking_id, customer_id=customer.customer_id, status="completed").first_or_404()

    data = request.get_json() or request.form
    score = float(data.get("rating_score", 0))
    comment = data.get("comment", "").strip()

    if not (1.0 <= score <= 5.0):
        return error("Rating must be between 1.0 and 5.0.")

    existing = Rating.query.filter_by(booking_id=booking_id).first()
    if existing:
        return error("You already rated this trip.")

    rating = Rating(
        booking_id=booking_id,
        customer_id=customer.customer_id,
        driver_id=booking.driver_id,
        rating_score=score,
        comment=comment,
    )
    db.session.add(rating)

    driver = Driver.query.get(booking.driver_id)
    if driver:
        all_ratings = Rating.query.filter_by(driver_id=driver.driver_id).all()
        all_scores = [r.rating_score for r in all_ratings] + [score]
        driver.rating = sum(all_scores) / len(all_scores)

    db.session.commit()
    return success(None, "Rating submitted.")


def _serialize_booking(b):
    """Serialize a booking for customer views."""
    return {
        "booking_id": b.booking_id,
        "pickup_address": b.pickup_address,
        "dropoff_address": b.dropoff_address,
        "scheduled_time": b.scheduled_time.isoformat() if b.scheduled_time else None,
        "estimated_cost": float(b.estimated_cost or 0),
        "status": b.status,
        "created_at": b.created_at.strftime("%Y-%m-%d") if b.created_at else "",
        "driver_name": b.driver.user.user_name if b.driver and b.driver.user else "",
        "plate_no": b.truck.plate_no if b.truck else "",
        "payment_status": b.payment.status if b.payment else None,
    }
