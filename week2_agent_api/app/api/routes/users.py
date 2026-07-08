from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas import ApiResponse, UserProfile
from app.utils.response import make_success_response

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


@router.get("/me", response_model=ApiResponse)
def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    """获取当前登录用户信息。

    这个接口属于用户资源，所以放在 users.py。
    """

    return make_success_response(current_user)
