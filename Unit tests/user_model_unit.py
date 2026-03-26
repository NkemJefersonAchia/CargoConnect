import models.customer  # noqa: F401
import models.driver  # noqa: F401
import models.notification  # noqa: F401
import models.truck  # noqa: F401
import models.booking  # noqa: F401
import models.payment  # noqa: F401
import models.rating  # noqa: F401
from models.user import User


def test_user_get_id_returns_string_value():
    user = User(user_id=42)

    assert user.get_id() == "42"