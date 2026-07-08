from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas import ApiResponse, LoginRequest, TokenData, UserProfile
from app.security.jwt import create_access_token
from app.services.auth_service import authenticate_user
from app.utils.response import make_success_response

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse)
def login(request: LoginRequest) -> ApiResponse:
    """
    登录接口

    登录成功后返回 access_token
    """

    user = authenticate_user(username=request.username, password=request.password)

    token = create_access_token(subject=user.username)

    data = TokenData(access_token=token, token_type="bearer")

    return make_success_response(data)


@router.get("/me", response_model=ApiResponse)
def get_me(current_user: UserProfile = Depends(get_current_user)) -> ApiResponse:
    """
    获取当前登录用户信息

    这个接口需要 Authorization 请求头。
    """

    return make_success_response(current_user)
