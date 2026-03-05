from datetime import datetime
from flask_login import UserMixin
from models import db


class User(UserMixin, db.Model):
    """User account shared across all roles."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_phone_no = db.Column(db.String(15))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("customer", "driver", "admin", name="user_role"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer_profile = db.relationship("Customer", backref="user", uselist=False, lazy=True)
    driver_profile = db.relationship("Driver", backref="user", uselist=False, lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)

    def get_id(self):
        """Return user_id as string for Flask-Login."""
        return str(self.user_id)
