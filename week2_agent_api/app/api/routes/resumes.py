from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.schemas import (
    ApiResponse,
    ResumeParseRequest,
    UserProfile,
    JobMatchRequest,
    JobMatchAnalysisRequest,
)
from app.services.resume_service import (
    parse_resume,
    save_resume_profile,
    list_current_user_resume_records,
    get_owned_resume_record,
    match_resume_with_jd,
    save_job_match_result,
    get_owend_job_match_record,
    build_job_match_analysis_prompt,
    generate_job_match_analysis,
    save_job_match_analysis,
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
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    data = get_owned_resume_record(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
    )
    return make_success_response(data)


@router.post("/{resume_id}/match", response_model=ApiResponse)
def match_resume(
    resume_id: int,
    request: JobMatchRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    """
    根据当前用户的一条简历记录和岗位 JD 做匹配分析。
    """

    data = match_resume_with_jd(
        db=db,
        user_id=current_user.id,
        resume_id=resume_id,
        jd_text=request.jd_text,
    )

    record = save_job_match_result(
        db=db,
        user_id=current_user.id,
        jd_text=request.jd_text,
        result_json=data,
    )

    return make_success_response(
        {
            "id": record.id,
            "result": data.model_dump(),
            "created_at": record.created_at,
        }
    )


@router.post("/job-matches/{match_id}/analysis", response_model=ApiResponse)
def analyze_job_match(
    match_id: int,
    request: JobMatchAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    match_record = get_owend_job_match_record(
        db=db,
        user_id=current_user.id,
        match_id=match_id,
    )

    prompt = build_job_match_analysis_prompt(match_record)

    analysis = generate_job_match_analysis(
        prompt,
        use_fake=request.use_fake,
    )

    saved_record = save_job_match_analysis(
        db=db,
        user_id=current_user.id,
        match_id=match_id,
        analysis=analysis,
    )

    return make_success_response(
        {
            "id": saved_record["id"],
            "analysis": saved_record["analysis"],
        }
    )
