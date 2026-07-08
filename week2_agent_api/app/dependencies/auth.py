from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
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
