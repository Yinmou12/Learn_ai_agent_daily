from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.schemas import (
    ApiResponse,
    InterviewQuestionCreate,
    QuestionSearchRequest,
    UserProfile,
)
from app.services.question_service import create_question, list_questions
from app.services.question_retrieval_service import (
    search_questions,
    save_question_search_records,
)
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
