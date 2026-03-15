from datetime import datetime
from decimal import Decimal
from models import db


class Booking(db.Model):
    # Core booking entity that connects customers, drivers, and trucks for cargo transport
    # Tracks all details from creation through completion of a cargo transportation job

    __tablename__ = "bookings"

    booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey("trucks.truck_id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)
    pickup_address = db.Column(db.Text, nullable=False)
    dropoff_address = db.Column(db.Text, nullable=False)
    dropoff_lat = db.Column(db.Float, nullable=True)   # GPS latitude of drop-off point (optional)
    dropoff_lng = db.Column(db.Float, nullable=True)   # GPS longitude of drop-off point (optional)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    estimated_cost = db.Column(db.Numeric(10, 2))
    status = db.Column(
        db.Enum("pending", "confirmed", "completed", "cancelled", name="booking_status"),
        default="pending",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to related models: payment, ratings, and truck details
    payment = db.relationship("Payment", backref="booking", uselist=False, lazy=True)
    ratings = db.relationship("Rating", backref="booking", lazy=True)
    truck = db.relationship("Truck", backref="bookings", lazy=True)
