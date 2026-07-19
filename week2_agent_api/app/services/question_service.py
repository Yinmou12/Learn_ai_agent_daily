import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion
from app.schemas import InterviewQuestionCreate, InterviewQuestionPublic


def to_question_public(question: InterviewQuestion) -> InterviewQuestionPublic:
    return InterviewQuestionPublic(
        id=question.id,
        question=question.question,
        reference_answer=question.reference_answer,
        key_points=json.loads(question.key_points_json),
        difficulty=question.difficulty,
        tags=json.loads(question.tags_json),
        created_at=question.created_at,
    )


def create_question(
    db: Session,
    question_create: InterviewQuestionCreate,
) -> InterviewQuestionPublic:
    question = InterviewQuestion(
        question=question_create.question,
        reference_answer=question_create.reference_answer,
        key_points_json=json.dumps(question_create.key_points, ensure_ascii=False),
        difficulty=question_create.difficulty,
        tags_json=json.dumps(question_create.tags, ensure_ascii=False),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return to_question_public(question)


def list_questions(
    db: Session,
    tag: str | None = None,
    difficulty: str | None = None,
) -> list[InterviewQuestionPublic]:

    if difficulty is None:
        statement = select(InterviewQuestion).order_by(InterviewQuestion.id.desc())
    else:
        statement = (
            select(InterviewQuestion)
            .where(InterviewQuestion.difficulty == difficulty)
            .order_by(InterviewQuestion.id.desc())
        )

    questions = db.scalars(statement).all()

    results: list[InterviewQuestionPublic] = []

    for question in questions:
        public_question = to_question_public(question)

        if tag is not None and tag not in public_question.tags:
            continue

        results.append(public_question)

    return results
