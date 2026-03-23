from datetime import datetime
from models import db


class Payment(db.Model):
    # Payment transaction record associated with a booking
    # Tracks payment method, amount, and completion timestamp

    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.booking_id"), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50), default="MTN_MOMO", nullable=False)
    status = db.Column(
        db.Enum("pending", "success", "failed", name="payment_status"),
        default="pending",
        nullable=False,
    )
    momo_reference_id = db.Column(db.String(100), nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
