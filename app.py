import eventlet
eventlet.monkey_patch()

from flask import Flask, redirect, url_for
from flask_login import current_user

from config.config import Config
from extensions import db, bcrypt, login_manager, socketio, migrate


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login session"""
        try:
            return User.query.get(int(user_id))
        except Exception:
            # DB temporarily unreachable — treat session as unauthenticated
            # rather than crashing the entire request with a 500.
            return None

    from routes.auth import auth_bp
    from routes.booking import booking_bp
    from routes.driver import driver_bp
    from routes.customer import customer_bp
    from routes.tracking import tracking_bp
    from routes.payment import payment_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(booking_bp, url_prefix="/booking")
    app.register_blueprint(driver_bp, url_prefix="/driver")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(tracking_bp)
    app.register_blueprint(payment_bp, url_prefix="/payment")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        """Redirect root to the appropriate dashboard based on role."""
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "driver":
                return redirect(url_for("driver.dashboard"))
            else:
                return redirect(url_for("customer.dashboard"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[WARNING] Could not create DB tables (is PostgreSQL running?): {e}")

    return app


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
