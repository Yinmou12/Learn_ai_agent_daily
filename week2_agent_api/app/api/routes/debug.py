from fastapi import APIRouter

from app.schemas import ApiResponse, DebugPing
from app.utils.response import make_success_response

router = APIRouter(prefix="/api/v1", tags=["debug"])


@router.get("/debug/ping", response_model=ApiResponse)
def debug_ping() -> ApiResponse:
    data = DebugPing(message="pong")
    return make_success_response(data)
