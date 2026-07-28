from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.schemas import (
    ApiResponse,
    InterviewQuestionCreate,
    QuestionSearchRequest,
    UserProfile,
    QuestionVectorSearchRequest,
)
from app.services.chroma_question_service import (
    search_questions_with_chroma,
    sync_questions_to_chroma,
    upsert_question_to_chroma,
)
from app.services.question_search_record_service import save_question_search_record
from app.services.question_service import create_question, list_questions
from app.services.question_retrieval_service import (
    search_questions,
    save_question_search_records,
)
from app.services.vector_retrieval_service import search_questions_by_vector
from app.utils.response import make_success_response

router = APIRouter(
    prefix="/api/v1/questions",
    tags=["questions"],
)


@router.post("", response_model=ApiResponse)
def create_intercview_question(
    request: InterviewQuestionCreate,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    data = create_question(
        db=db,
        question_create=request,
    )

    upsert_question_to_chroma(question=data)

    return make_success_response(data=data)


@router.get("", response_model=ApiResponse)
def get_interview_questions(
    tag: str | None = None,
    difficulty: str | None = None,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    data = list_questions(
        db=db,
        tag=tag.strip() if tag else None,
        difficulty=difficulty.strip() if difficulty else None,
    )
    return make_success_response(data=data)


@router.post("/search", response_model=ApiResponse)
def search_interview_questions(
    request: QuestionSearchRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:

    data = search_questions(
        db=db,
        request=request,
    )

    questions_id = save_question_search_records(
        db=db,
        user_id=current_user.id,
        request_json=request,
        search_results=data,
    )

    return make_success_response(
        data={
            "questions_id": questions_id,
            "items": data,
        }
    )


@router.post("/vector-search", response_model=ApiResponse)
def vector_search_interview_questions(
    request: QuestionVectorSearchRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    """使用本地向量基线检索面试题"""

    data = search_questions_by_vector(
        db=db,
        request=request,
    )

    save_question_search_record(
        db=db,
        user_id=current_user.id,
        request=request,
        search_results=data,
    )

    return make_success_response(data=data)


@router.post("/index", response_model=ApiResponse)
def index_interview_questions(
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(require_admin),
) -> ApiResponse:
    """把关系数据库题库同步到 Chroma"""

    data = sync_questions_to_chroma(db=db)

    return make_success_response(data=data)


@router.post("/chroma-search", response_model=ApiResponse)
def chroma_search_interview_questions(
    request: QuestionVectorSearchRequest,
    db: Session = Depends(get_db),
    current_user: UserProfile = Depends(get_current_user),
) -> ApiResponse:
    """使用真实 Embedding 和 Chroma 检索题目"""

    data = search_questions_with_chroma(
        db=db,
        request=request,
    )

    record_id = save_question_search_record(
        db=db,
        user_id=current_user.id,
        request=request,
        search_results=data,
    )

    return make_success_response(
        data={
            "record_id": record_id,
            "items": data,
        }
    )
