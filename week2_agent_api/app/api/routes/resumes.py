from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas import ApiResponse, ResumeParseRequest, UserProfile
from app.services.resume_service import parse_resume
from app.utils.response import make_success_response

router = APIRouter(
    prefix="/api/v1/resumes",
    tags=["resumes"],
)


@router.post("/parse", response_model=ApiResponse)
def parse_resume_api(
    request: ResumeParseRequest,
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    """
    解析简历文本

    当前接口需要登录
    后续会把解析结构保存到数据库
    """

    data = parse_resume(
        resume_text=request.resume_text,
        use_fake=request.use_fake,
    )

    return make_success_response(data=data)
