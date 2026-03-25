from datetime import datetime
from models import db


class Payment(db.Model):
    """Payment record for a booking."""

    __tablename__ = "payments"

    payment_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.booking_id"), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.String(50), default="MoMo")
    status = db.Column(
        db.Enum("pending", "paid", "failed", "success", name="payment_status"),
        default="pending",
    )
    paid_at = db.Column(db.DateTime, nullable=True)
