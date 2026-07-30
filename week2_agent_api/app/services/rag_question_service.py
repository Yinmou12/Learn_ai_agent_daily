import json
import re
from typing import Any

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.clients.llm_client import call_llm
from app.config import load_settings
from app.exceptions import RAGGenerationError
from app.schemas import (
    QuestionVectorSearchItem,
    QuestionVectorSearchRequest,
    RAGGeneratedQuestion,
    RAGQuestionGenerateRequest,
    RAGQuestionGenerationResult,
    RAGQuestionSet,
    RAGSource,
)
from app.services.chroma_question_service import search_questions_with_chroma


def build_rag_prompt(
    request: RAGQuestionGenerateRequest,
    retrieved_items: list[QuestionVectorSearchItem],
) -> str:
    """把检索的题目构造成受控上下文"""

    source_blocks: list[str] = []

    for item in retrieved_items:
        source = item.question

        # 对答案做长度限制，避免单条数据占用过多 Token
        reference_answer = source.reference_answer[:1200]

        source_blocks.append(
            "\n".join(
                [
                    f"[source_id={source.id}]",
                    f"题目：{source.question}",
                    f"参考答案：{reference_answer}",
                    f"关键点：{', '.join(source.key_points)}",
                    f"标签：{', '.join(source.tags)}",
                ]
            )
        )

    context = "\n\n".join(source_blocks)

    return f"""
你是 AI 模拟面试系统的出题模块。

请根据给定题库来源，为用户生成 {request.question_count} 道面试题。

要求：
1. 只能使用下面提供的题库来源。
2. 可以改写或组合题目，但不能引入来源中完全没有的技术主题。
3. 每道题必须包含 question、key_points、source_question_ids。
4. source_question_ids 只能使用上下文中的 source_id。
5. 只返回合法 JSON，不要返回 Markdown 或解释文字。

返回格式：
{{
  "topic": "本次面试主题",
  "questions": [
    {{
      "question": "生成后的面试题",
      "key_points": ["评分点一", "评分点二"],
      "source_question_ids": [1]
    }}
  ]
}}

用户需求：
{request.query}

题库来源：
{context}
""".strip()


def clean_json_response(raw_text: str) -> str:
    """兼容 LLM 偶尔返回的 Markdown JSON 代码围栏。"""

    text = raw_text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s*```$", "", text)

    return text.strip()


def parse_rag_question_set(
    raw_text: str,
    allowed_source_ids: set[int],
    expected_question_count: int,
) -> RAGQuestionSet:
    """解析并检查 LLM 的结构化出题结果。"""

    cleaned_text = clean_json_response(raw_text)

    try:
        data: dict[str, Any] = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise RAGGenerationError("LLM 返回的出题结果不是合法 JSON") from error

    try:
        result = RAGQuestionSet.model_validate(data)
    except ValidationError as error:
        raise RAGGenerationError(f"LLM 出题结果字段校验失败：{error}") from error

    if len(result.questions) != expected_question_count:
        raise RAGGenerationError("LLM 返回的题目数量与请求不一致")

    for generated_question in result.questions:
        source_ids = set(generated_question.source_question_ids)
        unknown_ids = source_ids - allowed_source_ids

        if unknown_ids:
            raise RAGGenerationError(
                f"LLM 引用了未检索到的来源：" f"{sorted(unknown_ids)}"
            )

    return result


def build_public_sources(
    retrieved_items: list[QuestionVectorSearchItem],
) -> list[RAGSource]:
    """隐藏参考答案，只公开来源题目和相似度。"""

    return [
        RAGSource(
            question_id=item.question.id,
            question=item.question.question,
            similarity=item.similarity,
        )
        for item in retrieved_items
    ]


def fake_generate_question_set(
    request: RAGQuestionGenerateRequest,
    retrieved_items: list[QuestionVectorSearchItem],
) -> RAGQuestionSet:
    """使用检索结果构造稳定的本地假数据"""

    selected_items = retrieved_items[: request.question_count]

    if len(selected_items) < request.question_count:
        raise RAGGenerationError("检索来源数量不足，无法生成指定数量的题目")

    questions = [
        RAGGeneratedQuestion(
            question=item.question.question,
            key_points=item.question.key_points,
            source_question_ids=[item.question.id],
        )
        for item in selected_items
    ]

    return RAGQuestionSet(
        topic=request.query,
        questions=questions,
    )


def generate_rag_question_set(
    db: Session,
    request: RAGQuestionGenerateRequest,
) -> RAGQuestionGenerationResult:
    """执行检索、上下文增强和题目生成。"""

    vector_request = QuestionVectorSearchRequest(
        query=request.query,
        tags=request.tags,
        difficulty=request.difficulty,
        top_k=request.source_top_k,
        min_similarity=request.min_similarity,
    )

    retrieved_items = search_questions_with_chroma(
        db=db,
        request=vector_request,
    )

    if not retrieved_items:
        raise RAGGenerationError("没有检索到可用于出题的题库来源")

    if request.use_fake:
        question_set = fake_generate_question_set(
            request=request,
            retrieved_items=retrieved_items,
        )
    else:
        prompt = build_rag_prompt(
            request=request,
            retrieved_items=retrieved_items,
        )
        settings = load_settings()

        raw_answer = call_llm(settings=settings, user_text=prompt)

        allowed_source_ids = {item.question.id for item in retrieved_items}

        question_set = parse_rag_question_set(
            raw_text=raw_answer,
            allowed_source_ids=allowed_source_ids,
            expected_question_count=request.question_count,
        )

    return RAGQuestionGenerationResult(
        topic=question_set.topic,
        questions=question_set.questions,
        sources=build_public_sources(retrieved_items),
    )
