from datetime import datetime
from models import db


class Notification(db.Model):
    # In-app notification message sent to a user
    # Tracks message content, delivery channel, and read status

    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
