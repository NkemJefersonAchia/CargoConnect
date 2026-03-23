from datetime import datetime
from decimal import Decimal
from models import db


class Booking(db.Model):
    # Core booking entity that connects customers, drivers, and trucks for cargo transport
    # Tracks all details from creation through completion of a cargo transportation job

    __tablename__ = "bookings"

    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id", ondelete="SET NULL"), nullable=True)
    truck_id = db.Column(db.Integer, db.ForeignKey("trucks.truck_id", ondelete="SET NULL"), nullable=True)
    pickup_address = db.Column(db.Text, nullable=False)
    dropoff_address = db.Column(db.Text, nullable=False)
    cargo_weight = db.Column(db.Float, nullable=False)
    estimated_cost = db.Column(db.Numeric(10, 2), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum("pending", "confirmed", "completed", "cancelled", name="booking_status"),
        default="pending",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to related models: payment, ratings, and truck details
    payment = db.relationship("Payment", backref="booking", uselist=False, lazy=True)
    ratings = db.relationship("Rating", backref="booking", lazy=True)
    truck = db.relationship("Truck", backref="bookings", lazy=True)
