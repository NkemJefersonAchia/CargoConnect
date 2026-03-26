from types import SimpleNamespace

from flask import Flask

import routes.payment as payment_module


def test_success_response_shape():
    app = Flask(__name__)
    with app.app_context():
        response = payment_module.success({"payment_id": 1}, "done")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "data": {"payment_id": 1},
        "message": "done",
    }


def test_error_response_shape_and_code():
    app = Flask(__name__)
    with app.app_context():
        response, code = payment_module.error("bad request", 422)

    assert code == 422
    assert response.get_json() == {
        "status": "error",
        "data": None,
        "message": "bad request",
    }


def test_get_momo_token_reads_access_token(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"access_token": "token-123"}

    def fake_post(url, auth, headers, timeout):
        assert url.endswith("/collection/token/")
        assert timeout == 10
        return DummyResponse()

    monkeypatch.setattr(payment_module.requests, "post", fake_post)

    token = payment_module.get_momo_token()
    assert token == "token-123"


def test_payment_callback_missing_reference_id():
    app = Flask(__name__)
    with app.test_request_context("/payment/callback", method="POST", json={}):
        response, code = payment_module.payment_callback()

    assert code == 400
    assert response.get_json()["message"] == "Missing reference ID."


def test_payment_callback_invalid_reference_id():
    app = Flask(__name__)
    with app.test_request_context(
        "/payment/callback", method="POST", json={"externalId": "abc"}
    ):
        response, code = payment_module.payment_callback()

    assert code == 400
    assert response.get_json()["message"] == "Invalid reference ID."


def test_payment_callback_record_not_found(monkeypatch):
    class DummyPaymentQuery:
        @staticmethod
        def filter_by(**kwargs):
            assert kwargs == {"booking_id": 99}
            return SimpleNamespace(first=lambda: None)

    monkeypatch.setattr(
        payment_module,
        "Payment",
        SimpleNamespace(query=DummyPaymentQuery()),
    )

    app = Flask(__name__)
    with app.test_request_context(
        "/payment/callback", method="POST", json={"externalId": "99"}
    ):
        response, code = payment_module.payment_callback()

    assert code == 404
    assert response.get_json()["message"] == "Payment record not found."
