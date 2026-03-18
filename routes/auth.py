from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import bcrypt
from models import db
from models.user import User
from models.customer import Customer
from models.driver import Driver

auth_bp = Blueprint("auth", __name__)


def create_response(status, data, message):
    """Return a standard JSON response envelope."""
    return jsonify({"status": status, "data": data, "message": message})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Show login form and authenticate user."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect_by_role(user.role)
        flash("Invalid email or password.", "danger")

    return render_template("client-login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Show registration form and create a new user account."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        full_name = (data.get("full_name") or data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        phone = (data.get("user_phone_no") or data.get("phone") or "").strip()
        password = data.get("password") or ""
        confirm_password = (
            data.get("confirm_password")
            or data.get("confirm-password")
            or data.get("confirmPassword")
            or ""
        )
        role = (data.get("role") or "customer").strip()

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("client-register.html")
        if not email:
            flash("Email is required.", "danger")
            return render_template("client-register.html")
        if not password:
            flash("Password is required.", "danger")
            return render_template("client-register.html")
        if confirm_password and password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("client-register.html")

        if role not in ("customer", "driver"):
            flash("Invalid role selected.", "danger")
            return render_template("client-register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("client-register.html")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user_name = (data.get("user_name") or "").strip() or full_name.split()[0]
        user = User(
            user_name=user_name,
            email=email,
            user_phone_no=phone,
            password_hash=password_hash,
            role=role,
            full_name=full_name,
        )
        db.session.add(user)
        db.session.flush()

        if role == "customer":
            profile = Customer(user_id=user.user_id)
            db.session.add(profile)
        elif role == "driver":
            licence_no = (data.get("licence_no") or "").strip()
            profile = Driver(user_id=user.user_id, licence_no=licence_no)
            db.session.add(profile)

        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("client-register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("auth.login"))


def redirect_by_role(role):
    """Redirect to the appropriate dashboard based on role."""
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "driver":
        return redirect(url_for("driver.dashboard"))
    return redirect(url_for("customer.dashboard"))
