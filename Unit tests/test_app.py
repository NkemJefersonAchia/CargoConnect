from app import create_app


def test_root_redirects_to_login_for_anonymous_user():
    app = create_app()
    client = app.test_client()

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth/login")