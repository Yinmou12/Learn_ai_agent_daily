from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas import ApiResponse, LoginRequest, TokenData, UserProfile, UserCreate
from app.security.jwt import create_access_token
from app.services.user_service import authenticate_user, create_user
from app.utils.response import make_success_response

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@router.post("/register", response_model=ApiResponse)
def register(request: UserCreate, db: Session = Depends(get_db)) -> ApiResponse:
    """
    注册接口
    """

    user = create_user(
        db=db,
        user_create=request,
    )

    return make_success_response(user)


@router.post("/login", response_model=ApiResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    登录接口

    登录成功后返回 access_token
    """

    user = authenticate_user(
        db=db,
        username=request.username,
        password=request.password,
    )

    token = create_access_token(subject=user.username)

    data = TokenData(
        access_token=token,
        token_type="bearer",
    )

    return make_success_response(data)
