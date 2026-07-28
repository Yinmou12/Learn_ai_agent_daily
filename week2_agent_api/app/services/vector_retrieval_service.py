import hashlib
import math
import re
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion
from app.schemas import (
    InterviewQuestionPublic,
    QuestionVectorSearchItem,
    QuestionVectorSearchRequest,
)
from app.services.question_service import to_question_public

VECTOR_DIMENSIONS = 256
TOKEN_PATTERN = re.compile(
    r"[a-z0-9_+#.-]+|[\u4e00-\u9fff]+",
    re.IGNORECASE,
)


def extract_vector_terms(text: str) -> list[str]:
    """提取英文技术词，并把较长中文片段拆成二元词组"""

    raw_terms = TOKEN_PATTERN.findall(text.casefold())
    terms: list[str] = []

    for term in raw_terms:
        is_chinese = all("\u4e00" <= character <= "\u9fff" for character in term)

        if not is_chinese:
            terms.append(term)
            continue

        terms.append(term)

        # 增加二元词组，例如"依赖注入"会产生"依赖","赖注","注入"
        if len(term) > 2:
            terms.extend(term[index : index + 2] for index in range(len(term) - 1))

    return terms


def stable_term_index(term: str, dimensions: int) -> int:
    """把同一个词稳定地映射到相同的向量位置"""

    if dimensions <= 0:
        raise ValueError("向量维度必须大于 0")

    digest = hashlib.sha256(term.encode("utf-8")).digest()
    number = int.from_bytes(digest[:8], byteorder="big")

    return number % dimensions


def vectorize_text(
    text: str,
    dimensions: int = VECTOR_DIMENSIONS,
) -> list[float]:
    """把文本转换成固定维度并完成归一化"""

    if dimensions <= 0:
        raise ValueError("向量维度必须大于 0")

    vector = [0.0] * dimensions
    terms = extract_vector_terms(text)

    if not terms:
        return vector

    for term in terms:
        index = stable_term_index(term, dimensions)
        vector[index] += 1.0

    # 计算向量长度
    vector_length = math.sqrt(sum(value * value for value in vector))

    if vector_length == 0:
        return vector

    # 归一化后,向量长度变成 1
    return [value / vector_length for value in vector]


def cosine_similarity(
    first: Sequence[float],
    second: Sequence[float],
) -> float:
    """计算余弦相似度"""

    if len(first) != len(second):
        raise ValueError("两个向量维度必须相同")

    first_length = math.sqrt(sum(value * value for value in first))
    secont_length = math.sqrt(sum(value * value for value in second))

    if first_length == 0 or secont_length == 0:
        return 0.0

    dot_product = sum(left * right for left, right in zip(first, second))

    return dot_product / (first_length * secont_length)


def build_question_document(question: InterviewQuestionPublic) -> str:
    """把一道结构化面试题转换成用于检索的文本"""

    return "\n".join(
        [
            question.question,
            question.reference_answer,
            " ".join(question.key_points),
            " ".join(question.tags),
        ]
    )


def search_questions_by_vector(
    db: Session,
    request: QuestionVectorSearchRequest,
) -> list[QuestionVectorSearchItem]:
    """使用本地 Hash 向量和余弦相似度检索题目"""

    statement = select(InterviewQuestion)

    if request.difficulty is not None:
        statement = statement.where(InterviewQuestion.difficulty == request.difficulty)

    question_models = db.scalars(statement).all()
    query_vector = vectorize_text(request.query)

    required_tags = {tag.casefold() for tag in request.tags}

    results: list[QuestionVectorSearchItem] = []

    for question_model in question_models:
        public_question = to_question_public(question_model)

        question_tags = {tag.casefold() for tag in public_question.tags}

        # 指定标签时，题目必须包含全部标签
        if not required_tags.issubset(question_tags):
            continue

        document = build_question_document(public_question)
        document_vector = vectorize_text(document)

        similarity = cosine_similarity(query_vector, document_vector)

        if similarity < request.min_similarity:
            continue

        results.append(
            QuestionVectorSearchItem(
                similarity=round(similarity, 4),
                question=public_question,
            )
        )

    results.sort(
        key=lambda item: (-item.similarity, -item.question.id),
    )

    return results[: request.top_k]
