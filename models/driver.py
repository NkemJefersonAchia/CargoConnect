from datetime import datetime
from models import db


class Driver(db.Model):
    """Driver profile linked to a user account."""

    __tablename__ = "drivers"

    driver_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    licence_no = db.Column(db.String(100), unique=True)
    rating = db.Column(db.Float, default=0.0)
    is_available = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trucks = db.relationship("Truck", backref="driver", lazy=True)
    bookings = db.relationship("Booking", backref="driver", lazy=True)
