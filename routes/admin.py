from functools import wraps
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.driver import Driver
from models.customer import Customer
from models.booking import Booking
from models.payment import Payment
from models.notification import Notification

admin_bp = Blueprint("admin", __name__)


def success(data, message="OK"):
    """Return a standard success JSON response."""
    return jsonify({"status": "success", "data": data, "message": message})


def error(message, code=400):
    """Return a standard error JSON response."""
    return jsonify({"status": "error", "data": None, "message": message}), code


def require_admin(f):
    """Decorator that restricts access to admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return error("Admin access required.", 403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/dashboard")
@login_required
@require_admin
def dashboard():
    """Render the admin dashboard page."""
    return render_template("admin_dashboard.html", user=current_user)


@admin_bp.route("/users-page")
@login_required
@require_admin
def users_page():
    """Render the admin users management page."""
    return render_template("admin_users.html", user=current_user)


@admin_bp.route("/drivers-page")
@login_required
@require_admin
def drivers_page():
    """Render the admin drivers management page."""
    return render_template("admin_drivers.html", user=current_user)


@admin_bp.route("/bookings-page")
@login_required
@require_admin
def bookings_page():
    """Render the admin bookings management page."""
    return render_template("admin_bookings.html", user=current_user)


@admin_bp.route("/payments-page")
@login_required
@require_admin
def payments_page():
    """Render the admin payments management page."""
    return render_template("admin_payments.html", user=current_user)


@admin_bp.route("/notifications-page")
@login_required
@require_admin
def notifications_page():
    """Render the admin notifications page."""
    return render_template("admin_notifications.html", user=current_user)


@admin_bp.route("/stats", methods=["GET"])
@login_required
@require_admin
def stats():
    """Return platform-wide statistics."""
    total_users = User.query.count()
    total_drivers = Driver.query.count()
    verified_drivers = Driver.query.filter_by(is_verified=True).count()
    total_bookings = Booking.query.count()
    completed_bookings = Booking.query.filter_by(status="completed").count()
    total_revenue = db.session.query(db.func.sum(Booking.estimated_cost)).filter(
        Booking.status == "completed"
    ).scalar() or 0

    return success({
        "total_users": total_users,
        "total_drivers": total_drivers,
        "verified_drivers": verified_drivers,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "total_revenue": float(total_revenue),
    })


@admin_bp.route("/unverified-drivers", methods=["GET"])
@login_required
@require_admin
def unverified_drivers():
    """Return all drivers pending verification."""
    drivers = Driver.query.filter_by(is_verified=False).all()
    return success([_serialize_driver(d) for d in drivers])


@admin_bp.route("/drivers/<int:driver_id>/verify", methods=["POST"])
@login_required
@require_admin
def verify_driver(driver_id):
    """Verify a driver account."""
    driver = Driver.query.get_or_404(driver_id)
    driver.is_verified = True
    note = Notification(
        user_id=driver.user_id,
        message="Your driver account has been verified. You can now go online.",
        channel="in-app",
    )
    db.session.add(note)
    db.session.commit()
    return success(None, "Driver verified.")


@admin_bp.route("/drivers/<int:driver_id>/reject", methods=["DELETE"])
@login_required
@require_admin
def reject_driver(driver_id):
    """Reject and remove an unverified driver."""
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    return success(None, "Driver rejected and removed.")


@admin_bp.route("/users", methods=["GET"])
@login_required
@require_admin
def list_users():
    """Return all users."""
    users = User.query.order_by(User.created_at.desc()).all()
    return success([_serialize_user(u) for u in users])


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
@require_admin
def delete_user(user_id):
    """Delete a user account."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return success(None, "User deleted.")


@admin_bp.route("/drivers", methods=["GET"])
@login_required
@require_admin
def list_drivers():
    """Return all driver records."""
    drivers = Driver.query.all()
    return success([_serialize_driver(d) for d in drivers])


@admin_bp.route("/drivers/<int:driver_id>/toggle-availability", methods=["PATCH"])
@login_required
@require_admin
def toggle_driver_availability(driver_id):
    """Toggle a driver's availability."""
    driver = Driver.query.get_or_404(driver_id)
    driver.is_available = not driver.is_available
    db.session.commit()
    return success({"is_available": driver.is_available}, "Availability toggled.")


@admin_bp.route("/drivers/<int:driver_id>/remove-verification", methods=["PATCH"])
@login_required
@require_admin
def remove_verification(driver_id):
    """Remove verification from a driver."""
    driver = Driver.query.get_or_404(driver_id)
    driver.is_verified = False
    db.session.commit()
    return success(None, "Verification removed.")


@admin_bp.route("/drivers/<int:driver_id>", methods=["DELETE"])
@login_required
@require_admin
def delete_driver(driver_id):
    """Delete a driver record."""
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    return success(None, "Driver deleted.")


@admin_bp.route("/bookings", methods=["GET"])
@login_required
@require_admin
def list_bookings():
    """Return all bookings, optionally filtered by status."""
    status_filter = request.args.get("status")
    query = Booking.query.order_by(Booking.created_at.desc())
    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)
    bookings = query.all()
    return success([_serialize_booking(b) for b in bookings])


@admin_bp.route("/payments", methods=["GET"])
@login_required
@require_admin
def list_payments():
    """Return all payment records, optionally filtered by status."""
    status_filter = request.args.get("status")
    query = Payment.query.order_by(Payment.payment_id.desc())
    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)
    payments = query.all()
    return success([_serialize_payment(p) for p in payments])


@admin_bp.route("/all-notifications", methods=["GET"])
@login_required
@require_admin
def list_all_notifications():
    """Return the 100 most recent platform notifications."""
    notes = Notification.query.order_by(Notification.sent_at.desc()).limit(100).all()
    return success([_serialize_notification(n) for n in notes])


def _serialize_user(u):
    """Serialize a user record to dict."""
    return {
        "user_id": u.user_id,
        "user_name": u.user_name,
        "email": u.email,
        "user_phone_no": u.user_phone_no,
        "role": u.role,
        "created_at": u.created_at.strftime("%Y-%m-%d") if u.created_at else "",
    }


def _serialize_driver(d):
    """Serialize a driver record to dict."""
    truck = d.trucks[0] if d.trucks else None
    return {
        "driver_id": d.driver_id,
        "user_id": d.user_id,
        "name": d.user.user_name,
        "email": d.user.email,
        "phone": d.user.user_phone_no,
        "licence_no": d.licence_no,
        "rating": d.rating,
        "is_available": d.is_available,
        "is_verified": d.is_verified,
        "plate_no": truck.plate_no if truck else None,
        "created_at": d.user.created_at.strftime("%Y-%m-%d") if d.user.created_at else "",
    }


def _serialize_booking(b):
    """Serialize a booking record for admin views."""
    payment = b.payment
    return {
        "booking_id": b.booking_id,
        "customer_name": b.customer.user.user_name if b.customer else "",
        "driver_name": b.driver.user.user_name if b.driver else "",
        "pickup_address": b.pickup_address,
        "dropoff_address": b.dropoff_address,
        "scheduled_time": b.scheduled_time.isoformat() if b.scheduled_time else None,
        "status": b.status,
        "estimated_cost": float(b.estimated_cost or 0),
        "created_at": b.created_at.strftime("%Y-%m-%d") if b.created_at else "",
        "plate_no": b.truck.plate_no if b.truck else "",
        "payment_status": payment.status if payment else None,
    }


def _serialize_payment(p):
    """Serialize a payment record for admin views."""
    booking = p.booking
    return {
        "payment_id": p.payment_id,
        "booking_id": p.booking_id,
        "amount": float(p.amount or 0),
        "method": p.method or "MoMo",
        "status": p.status,
        "paid_at": p.paid_at.strftime("%Y-%m-%d %H:%M") if p.paid_at else None,
        "customer_name": booking.customer.user.user_name if booking and booking.customer else "—",
        "driver_name": booking.driver.user.user_name if booking and booking.driver else "—",
    }


def _serialize_notification(n):
    """Serialize a notification record for admin views."""
    return {
        "notification_id": n.notification_id,
        "user_name": n.user.user_name if n.user else "—",
        "user_role": n.user.role if n.user else "—",
        "message": n.message,
        "channel": n.channel or "in-app",
        "is_read": n.is_read,
        "sent_at": n.sent_at.strftime("%Y-%m-%d %H:%M") if n.sent_at else "",
    }
