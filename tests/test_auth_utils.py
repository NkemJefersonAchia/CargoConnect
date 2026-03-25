from flask import Blueprint, Flask

from routes.auth import create_response, redirect_by_role


def build_app_with_dashboards():
    app = Flask(__name__)
    app.secret_key = "test-secret"

    admin_bp = Blueprint("admin", __name__)
    driver_bp = Blueprint("driver", __name__)
    customer_bp = Blueprint("customer", __name__)

    @admin_bp.route("/dashboard")
    def dashboard():
        return "admin"

    @driver_bp.route("/dashboard", endpoint="dashboard")
    def dashboard_driver():
        return "driver"

    @customer_bp.route("/dashboard", endpoint="dashboard")
    def dashboard_customer():
        return "customer"

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(driver_bp, url_prefix="/driver")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    return app


def test_create_response_wraps_payload():
    app = Flask(__name__)
    with app.app_context():
        response = create_response("success", {"x": 1}, "ok")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "data": {"x": 1},
        "message": "ok",
    }


def test_redirect_by_role_admin():
    app = build_app_with_dashboards()
    with app.test_request_context("/"):
        response = redirect_by_role("admin")

    assert response.location.endswith("/admin/dashboard")


def test_redirect_by_role_driver():
    app = build_app_with_dashboards()
    with app.test_request_context("/"):
        response = redirect_by_role("driver")

    assert response.location.endswith("/driver/dashboard")


def test_redirect_by_role_defaults_to_customer():
    app = build_app_with_dashboards()
    with app.test_request_context("/"):
        response = redirect_by_role("customer")

    assert response.location.endswith("/customer/dashboard")
