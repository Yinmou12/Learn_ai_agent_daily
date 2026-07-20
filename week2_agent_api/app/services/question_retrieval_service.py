import re
import json

import logging

search_logger = logging.getLogger("app.question_search")

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion
from app.models.question_search_records import QuestionSearch
from app.schemas import (
    InterviewQuestionPublic,
    QuestionSearchRequest,
    QuestionSearchItem,
)
from app.services.question_service import to_question_public


def extract_query_terms(query: str) -> list[str]:
    """
    从查询文本中提取英文技术词和连续中文词

    当前版本是关键词基线，不是专业分词器
    输入关键词时建议用空格分隔，例如：
    FastAPI Depends 依赖注入
    """

    normalized_query = query.casefold()

    """
    第二部分
        ` [\u4e00-\u9fff] ` 
            是一个 Unicode 范围，它覆盖了绝大部分常用的 CJK (中日韩) 统一表意文字，也就是我们常说的汉字。
        
        ` {2,} `
            一个量词，表示匹配前面的字符至少 2 次。
    这部分会匹配由两个或更多连续汉字组成的词语。例如，“依赖注入”会被匹配，但单个的“和”字则不会被匹配。
    """
    raw_terms = re.findall(
        r"[a-z0-9_+#.-]+|[\u4e00-\u9fff]{2,}",
        normalized_query,
    )

    # dict 保留插入顺序，可以在去重后保持原来的关键词顺序
    return list(dict.fromkeys(raw_terms))


def calculate_question_score(
    question: InterviewQuestionPublic,
    query_terms: list[str],
    requested_tags: list[str],
) -> tuple[int, list[str]]:
    """计算一道面试题与检索请求的相关性分数"""

    question_text = question.question.casefold()
    answer_text = question.reference_answer.casefold()
    key_points_text = " ".join(question.key_points).casefold()

    question_tags = {tag.casefold() for tag in question.tags}
    normalized_requested_tags = {tag.casefold() for tag in requested_tags}

    if not normalized_requested_tags.issubset(question_tags):
        return 0, []

    score = len(normalized_requested_tags) * 6
    matched_terms: list[str] = sorted(normalized_requested_tags)

    for term in query_terms:
        term_score = 0

        if term in question_text:
            term_score += 5

        if any(term in tag for tag in question_tags):
            term_score += 4

        if term in key_points_text:
            term_score += 3

        if term in answer_text:
            term_score += 1

        if term_score > 0:
            score += term_score
            matched_terms.append(term)

    # 同一个词可能同时作为查询词和标签出现，这里统一去重
    unique_matched_terms = list(dict.fromkeys(matched_terms))

    return score, unique_matched_terms


def search_questions(
    db: Session,
    request: QuestionSearchRequest,
) -> list[QuestionSearchItem]:

    statement = select(InterviewQuestion)

    if request.difficulty is not None:
        statement = select(InterviewQuestion).where(
            InterviewQuestion.difficulty == request.difficulty
        )

    questions = db.scalars(statement).all()
    query_terms = extract_query_terms(request.query)

    results: list[QuestionSearchItem] = []
    for question_model in questions:
        public_question = to_question_public(question_model)

        score, matched_terms = calculate_question_score(
            question=public_question,
            query_terms=query_terms,
            requested_tags=request.tags,
        )

        if score <= request.min_score:
            continue

        results.append(
            QuestionSearchItem(
                score=score,
                matched_terms=matched_terms,
                question=public_question,
            )
        )

    results.sort(key=lambda item: (-item.score, -item.question.id))
    final_results = results[: request.top_k]

    search_logger.info(
        "question_search query=%s query_terms=%s candidate_count=%s returned_count=%s difficulty=%s tags=%s top_k=%s",
        request.query,
        query_terms,
        len(questions),
        len(final_results),
        request.difficulty,
        request.tags,
        request.top_k,
    )

    return final_results


def save_question_search_records(
    db: Session,
    user_id: int,
    request_json: QuestionSearchRequest,
    search_results: list[QuestionSearchItem],
) -> list[int]:

    result_data = []
    questions_id = []
    for item in search_results:
        item_data = item.model_dump()
        item_data["question"].pop("created_at", None)
        result_data.append(item_data)
        questions_id.append(item_data["question"]["id"])

    record = QuestionSearch(
        user_id=user_id,
        request_body=request_json.model_dump_json(),
        search_questions_result=json.dumps(
            result_data,
            ensure_ascii=False,
        ),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return questions_id
