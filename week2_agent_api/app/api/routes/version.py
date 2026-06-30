from fastapi import APIRouter, Request

from app.schemas import ApiResponse, VersionData
from app.utils.response import make_success_response

router = APIRouter(prefix="/api/v1", tags=["version"])


@router.get("/version", response_model=ApiResponse)
def get_version(request: Request) -> ApiResponse:
    """
    查询服务版本号

    这里通过 request.app.version 读取 FastAPI 应用版本。
    这样 version 只需要在 main.py 里维护一份
    """

    data = VersionData(version=request.app.version)
    return make_success_response(data)
