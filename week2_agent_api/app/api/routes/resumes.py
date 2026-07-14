from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.schemas import ApiResponse, ResumeParseRequest, UserProfile, ResumeRecordPublic
from app.services.resume_service import (
    parse_resume,
    save_resume_profile,
    list_current_user_resume_records,
    search_resume_record_by_id,
)
from app.utils.response import make_success_response

router = APIRouter(
    prefix="/api/v1/resumes",
    tags=["resumes"],
)


@router.post("/parse")
def parse_resume_api(
    request: ResumeParseRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    解析简历文本

    当前接口需要登录
    把解析结构保存到数据库
    """

    profile = parse_resume(
        resume_text=request.resume_text,
        use_fake=request.use_fake,
    )

    record = save_resume_profile(
        db=db,
        user_id=current_user.id,
        raw_text=request.resume_text,
        profile=profile,
    )

    return make_success_response(
        data={
            "id": record.id,
            "profile": profile.model_dump(),
        }
    )


@router.get("", response_model=ApiResponse)
def get_resumes_record(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    data = list_current_user_resume_records(
        db=db,
        user_id=current_user.id,
    )

    return make_success_response(data)


@router.get("/{resume_id}", response_model=ApiResponse)
def get_resume_record_by_id(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    data = search_resume_record_by_id(
        db=db,
        user_id=current_user.id,
    )
    return make_success_response(data)
