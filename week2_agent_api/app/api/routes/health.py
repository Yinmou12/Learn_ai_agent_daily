from fastapi import APIRouter

from app.schemas import ApiResponse, HealthResponse
from app.utils.response import make_success_response

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse)
def health_check() -> ApiResponse:
    """
    健康检查接口

    这个接口用于确认服务是否正常启动。
    一般不会写复杂业务逻辑，只返回服务状态。
    """

    data = HealthResponse(status="ok", service="agent-backend-api")
    return make_success_response(data)
