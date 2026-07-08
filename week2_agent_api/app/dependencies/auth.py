from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import UserProfile
from app.security.jwt import decode_access_token
from app.services.auth_service import get_user_by_username

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> UserProfile:
    """
    从 Authorization 请求头中解析当前用户

    HTTPBearer 会读取：
    Authorization: Bearer <token>
    """

    token = credentials.credentials
    username = decode_access_token(token)

    return get_user_by_username(username)
