from models import db


class Truck(db.Model):
    """Truck registered under a driver."""

    __tablename__ = "trucks"

    truck_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)
    plate_no = db.Column(db.String(100), unique=True)
    capacity = db.Column(db.Float)  # stored in tons
