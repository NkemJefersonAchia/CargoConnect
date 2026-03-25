from models.user import User


def test_user_get_id_returns_string_value():
    user = User(user_id=42)

    assert user.get_id() == "42"