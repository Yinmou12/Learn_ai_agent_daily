from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas import ApiResponse, UserProfile
from app.services.user_service import (
    list_users,
    get_user_info,
    update_user_display_name,
)
from app.utils.response import make_success_response, make_error_response

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


@router.get("", response_model=ApiResponse)
def get_users(
    page: int = Query(default=1, ge=1, description="页码,从 1 开始"),
    page_size: int = Query(default=10, ge=1, le=100, description="每页数量"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    分页获取用户列表。

    current_user 当前暂时没有直接使用。
    但它的存在表示：这个接口必须登录后才能访问。
    """

    data = list_users(
        db=db,
        page=page,
        page_size=page_size,
    )

    return make_success_response(data)


@router.get("/{search_user}", response_model=ApiResponse)
def get_user(
    username: str = None,
    user_id: int = None,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    查询单个用户
    """

    data = get_user_info(
        db=db,
        username=username,
        user_id=user_id,
    )

    return make_success_response(data)


@router.put("/me", response_model=ApiResponse)
def update_current_user_display_name(
    update_display_name: str,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse:
    """
    更新当前用户展示名称
    """

    data = update_user_display_name(
        db=db,
        username=current_user.username,
        display_name=update_display_name,
    )

    return make_success_response(data)
