from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import load_settings
from app.exceptions import AuthError


def create_access_token(subject: str) -> str:
    """
    创建 JWT token。

    subject 通常放用户唯一标识。
    今天先放 username。
    """

    settings = load_settings()

    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )

    payload: dict[str, any] = {
        "sub": subject,
        "exp": expire_at,
    }

    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> str:
    """
    解析 JWT token,并返回 username
    """

    settings = load_settings()

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as error:
        raise AuthError("token 已过期") from error
    except jwt.InvalidTokenError as error:
        raise AuthError("token 无效") from error

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise AuthError("token 缺少用户标识")

    return subject
