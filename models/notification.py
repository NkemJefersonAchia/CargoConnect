from datetime import datetime
from models import db


class Notification(db.Model):
    # notification message sent to a user
    # Tracks message content, delivery channel, and read status

    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.booking_id", ondelete="SET NULL"), nullable=True)
    message = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(50), default="in_app", nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
