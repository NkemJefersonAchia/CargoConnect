from datetime import datetime
from models import db


class Rating(db.Model):
    # Customer review and rating for a driver after a completed booking
    # Recording feedback score and optional comment about the delivery service

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.booking_id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)
    # Rating score from 1.0 to 5.0
    rating_score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
