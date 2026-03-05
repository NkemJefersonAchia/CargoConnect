from models import db


class Customer(db.Model):
    """Customer profile linked to a user account."""

    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    default_address = db.Column(db.Text, nullable=True)

    bookings = db.relationship("Booking", backref="customer", lazy=True)
