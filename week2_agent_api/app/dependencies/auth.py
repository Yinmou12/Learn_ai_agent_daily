from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.exceptions import PermissionDeniedError
from app.schemas import UserProfile
from app.security.jwt import decode_access_token
from app.services.user_service import get_user_by_username

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserProfile:
    """
    从 Authorization 请求头中解析当前用户
    """

    token = credentials.credentials
    username = decode_access_token(token)

    return get_user_by_username(
        db=db,
        username=username,
    )


def require_admin(
    current_user: UserProfile = Depends(get_current_user),
) -> UserProfile:
    """要求当前登录用户必须是管理员"""

    if not current_user.is_admin:
        raise PermissionDeniedError("该操作需要管理员权限")

    return current_user
