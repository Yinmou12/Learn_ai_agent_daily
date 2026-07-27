import json
from collections.abc import Sequence

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.question_search_records import QuestionSearch


def save_question_search_record(
    db: Session,
    user_id: int,
    request: BaseModel,
    search_results: Sequence[BaseModel],
) -> int:
    """
    保存任意一种题库检索请求和结果。

    使用 BaseModel 是因为关键词检索和向量检索
    都使用 Pydantic Schema，但具体类型不同。
    """

    result_data = [item.model_dump(mode="json") for item in search_results]

    record = QuestionSearch(
        user_id=user_id,
        request_body=request.model_dump_json(),
        search_questions_result=json.dumps(result_data, ensure_ascii=False),
    )

    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except SQLAlchemyError:
        db.rollback()
        raise

    return record.id
