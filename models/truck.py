from models import db


class Truck(db.Model):
    # Truck vehicle registered and owned by a driver
    # Tracks truck details including identification and cargo capacity

    __tablename__ = "trucks"

    truck_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)
    plate_no = db.Column(db.String(100), unique=True)
    # Cargo capacity measured in tons
    capacity = db.Column(db.Float)
