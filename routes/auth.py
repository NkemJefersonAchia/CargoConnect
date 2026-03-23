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
    if request.method == "GET" and current_user.is_authenticated:
        return redirect_by_role(current_user.role)

    if request.method == "POST":
        print("\n" + "="*60)
        print("[LOGIN] POST received")
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        print(f"[LOGIN] Email: {email}")

        user = User.query.filter_by(email=email).first()
        print(f"[LOGIN] User found: {user is not None}")
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            print(f"[LOGIN] SUCCESS — logged in user_id={user.user_id}, role={user.role}")
            print("="*60 + "\n")
            return redirect_by_role(user.role)
        print(f"[LOGIN] FAILED — invalid credentials")
        print("="*60 + "\n")
        flash("Invalid email or password.", "danger")

    return render_template("client-login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Show registration form and create a new user account."""
    # If already logged in, log out first so they can register a new account
    if current_user.is_authenticated:
        logout_user()

    if request.method == "POST":
        print("\n" + "="*60)
        print("[REGISTER] POST received")
        print(f"[REGISTER] Form data: {dict(request.form)}")

        user_name = request.form.get("user_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "customer")

        print(f"[REGISTER] name={user_name}, email={email}, phone={phone}, role={role}")

        if role not in ("customer", "driver"):
            print(f"[REGISTER] REJECTED — invalid role: {role}")
            flash("Invalid role selected.", "danger")
            return render_template(_register_template(role))

        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"[REGISTER] REJECTED \u2014 email already exists (user_id={existing.user_id})")
            flash("Email already registered.", "danger")
            return render_template(_register_template(role))

        try:
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
            print(f"[REGISTER] User flushed — user_id={user.user_id}")

            if role == "customer":
                profile = Customer(user_id=user.user_id)
                db.session.add(profile)
                print(f"[REGISTER] Customer profile created")
            elif role == "driver":
                licence_no = request.form.get("licence_no", "").strip()
                profile = Driver(user_id=user.user_id, licence_no=licence_no)
                db.session.add(profile)
                print(f"[REGISTER] Driver profile created, licence={licence_no}")

            db.session.commit()
            print(f"[REGISTER] COMMIT SUCCESS — user saved to database!")
            print("="*60 + "\n")
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            print(f"[REGISTER] ERROR — {type(e).__name__}: {e}")
            print("="*60 + "\n")
            flash(f"Registration error: {e}", "danger")
            return render_template(_register_template(role))

    role = request.args.get("role", "customer")
    if role == "driver":
        return render_template("driver-register.html")
    return render_template("client-register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("auth.login"))


def _register_template(role):
    """Return the correct register template for the given role."""
    return "driver-register.html" if role == "driver" else "client-register.html"


def redirect_by_role(role):
    """Redirect to the appropriate dashboard based on role."""
    if role == "admin":
        return redirect(url_for("admin.dashboard"))
    elif role == "driver":
        return redirect(url_for("driver.dashboard"))
    return redirect(url_for("customer.dashboard"))