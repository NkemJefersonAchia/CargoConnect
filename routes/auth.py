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
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect_by_role(user.role)
        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Show registration form and create a new user account."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == "POST":
        user_name = request.form.get("user_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("user_phone_no", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")

        if role not in ("customer", "driver"):
            flash("Invalid role selected.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            user_name=user_name,
            email=email,
            user_phone_no=phone,
            password_hash=password_hash,
            role=role,
        )
        db.session.add(user)
        db.session.flush()

        if role == "customer":
            profile = Customer(user_id=user.user_id)
            db.session.add(profile)
        elif role == "driver":
            licence_no = request.form.get("licence_no", "").strip()
            profile = Driver(user_id=user.user_id, licence_no=licence_no)
            db.session.add(profile)

        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


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
