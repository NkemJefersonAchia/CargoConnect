import uuid
import requests
import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.booking import Booking
from models.payment import Payment
from models.notification import Notification

payment_bp = Blueprint("payment", __name__)


def success(data, message="OK"):
    """Return a standard success JSON response."""
    return jsonify({"status": "success", "data": data, "message": message})


def error(message, code=400):
    """Return a standard error JSON response."""
    return jsonify({"status": "error", "data": None, "message": message}), code


def get_momo_token():
    """Obtain an access token from the MoMo collections API."""
    base_url = os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
    user_id = os.getenv("MOMO_USER_ID", "")
    api_key = os.getenv("MOMO_API_KEY", "")
    subscription_key = os.getenv("MOMO_SUBSCRIPTION_KEY", "")

    response = requests.post(
        f"{base_url}/collection/token/",
        auth=(user_id, api_key),
        headers={"Ocp-Apim-Subscription-Key": subscription_key},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("access_token")


@payment_bp.route("/initiate/<int:booking_id>", methods=["POST"])
@login_required
def initiate_payment(booking_id):
    """Initiate an MTN MoMo payment for a booking."""
    booking = Booking.query.get_or_404(booking_id)
    customer_phone = booking.customer.user.user_phone_no

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        payment = Payment(
            booking_id=booking_id,
            amount=booking.estimated_cost or 0,
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()

    reference = str(booking_id)
    base_url = os.getenv("MOMO_BASE_URL", "https://sandbox.momodeveloper.mtn.com")
    subscription_key = os.getenv("MOMO_SUBSCRIPTION_KEY", "")

    try:
        token = get_momo_token()
        payload = {
            "amount": str(int(booking.estimated_cost or 0)),
            "currency": "RWF",
            "externalId": reference,
            "payer": {"partyIdType": "MSISDN", "partyId": customer_phone},
            "payerMessage": f"CargoConnect booking #{booking_id}",
            "payeeNote": f"Payment for trip #{booking_id}",
        }
        resp = requests.post(
            f"{base_url}/collection/v1_0/requesttopay",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Reference-Id": reference,
                "X-Target-Environment": "sandbox",
                "Ocp-Apim-Subscription-Key": subscription_key,
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        if resp.status_code == 202:
            return success({"payment_id": payment.payment_id}, "Payment request sent to customer phone.")
        else:
            return error(f"MoMo API error: {resp.text}", 502)

    except requests.RequestException:
        note = Notification(
            user_id=booking.customer.user_id,
            message=f"Payment for booking #{booking_id} could not be processed. Please retry.",
            channel="in-app",
        )
        db.session.add(note)
        db.session.commit()
        return error("MoMo service unavailable. You will be notified to retry.", 503)


@payment_bp.route("/simulate/<int:booking_id>", methods=["POST"])
@login_required
def simulate_payment(booking_id):
    """Simulate an MTN MoMo payment (demo mode — no real API call)."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.customer.user_id != current_user.user_id:
        return error("Not authorised.", 403)

    if not booking.driver:
        return error("No driver has been assigned to this booking yet.")

    if booking.status not in ("confirmed", "completed", "pending"):
        return error("Booking cannot be paid at this stage.")

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        payment = Payment(
            booking_id=booking_id,
            amount=booking.estimated_cost or 0,
            status="pending",
        )
        db.session.add(payment)
        db.session.flush()

    if payment.status == "paid":
        return error("This booking has already been paid.")

    payment.status = "paid"
    payment.paid_at = datetime.utcnow()

    note_customer = Notification(
        user_id=booking.customer.user_id,
        message=(
            f"Payment of {int(booking.estimated_cost or 0):,} RWF for booking "
            f"#{booking_id} received via MTN MoMo. Thank you!"
        ),
        channel="in-app",
    )
    note_driver = Notification(
        user_id=booking.driver.user_id,
        message=(
            f"MTN MoMo payment for booking #{booking_id} has been confirmed. "
            f"Amount: {int(booking.estimated_cost or 0):,} RWF."
        ),
        channel="in-app",
    )
    db.session.add(note_customer)
    db.session.add(note_driver)
    db.session.commit()

    return success(
        {"payment_id": payment.payment_id, "status": "paid"},
        "Payment successful.",
    )


@payment_bp.route("/callback", methods=["POST"])
def payment_callback():
    """Handle MTN MoMo payment status callback."""
    data = request.get_json() or {}
    reference_id = data.get("externalId") or data.get("financialTransactionId")
    status = data.get("status", "").upper()

    if not reference_id:
        return error("Missing reference ID.", 400)

    try:
        booking_id = int(reference_id)
    except ValueError:
        return error("Invalid reference ID.", 400)

    payment = Payment.query.filter_by(booking_id=booking_id).first()
    if not payment:
        return error("Payment record not found.", 404)

    booking = Booking.query.get(booking_id)

    if status == "SUCCESSFUL":
        payment.status = "paid"
        payment.paid_at = datetime.utcnow()
        db.session.commit()

        if booking:
            note_customer = Notification(
                user_id=booking.customer.user_id,
                message=f"Payment for booking #{booking_id} received successfully.",
                channel="in-app",
            )
            note_driver = Notification(
                user_id=booking.driver.user_id,
                message=f"Payment for booking #{booking_id} has been confirmed.",
                channel="in-app",
            )
            db.session.add(note_customer)
            db.session.add(note_driver)
            db.session.commit()
    elif status == "FAILED":
        payment.status = "failed"
        db.session.commit()

        if booking:
            note = Notification(
                user_id=booking.customer.user_id,
                message=f"Payment for booking #{booking_id} failed. Please retry.",
                channel="in-app",
            )
            db.session.add(note)
            db.session.commit()

    return success(None, "Callback processed.")
