from hmac import compare_digest

from app.exceptions import AuthError
from app.schemas import UserProfile
from app.security.password import verify_password

DEMO_USERS: dict[str, dict[str, str]] = {
    "demo": {
        "password": "551956e28f0f28d074e3f25ab7283dc1$6813fdc63063c1fc7f77ba31f159dba82df5ca2ef0fe13cb935b9206723c995e",
        "display_name": "Demo User",
    }
}


def authenticate_user(username: str, password: str) -> UserProfile:
    """
    校验用户名和密码。

    今天先用内存假用户。
    后面接数据库后，会从 user 表查询用户。
    """

    user = DEMO_USERS.get(username)

    if user is None:
        raise AuthError("用户名或密码错误")

    # compare_digest 用于更安全地比较字符串
    if not verify_password(password, user["password"]):
        raise AuthError("用户名或密码错误")

    return UserProfile(username=username, display_name=user["display_name"])


def get_user_by_username(username: str) -> UserProfile:
    """
    根据 username 获取用户信息。
    """

    user = DEMO_USERS.get(username)

    if user is None:
        raise AuthError("用户不存在")

    return UserProfile(
        username=username,
        display_name=user["display_name"],
    )
