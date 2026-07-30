import json
from functools import lru_cache
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import load_settings
from app.exceptions import VectorStoreError
from app.models.interview_question import InterviewQuestion
from app.schemas import (
    QuestionVectorSearchItem,
    QuestionVectorSearchRequest,
    InterviewQuestionPublic,
)
from app.services.question_service import to_question_public
from app.services.vector_retrieval_service import build_question_document

COLLECTION_NAME = "interview_questions_v1"


@lru_cache(maxsize=1)
def get_question_collection() -> Collection:
    """
    创建或读取面试题 Collection。

    lru_cache 保证同一进程中不反复加载本地模型
    """

    settings = load_settings()

    try:
        client = chromadb.PersistentClient(path=settings.chroma_path)

        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model,
            device="cpu",
            normalize_embeddings=True,
            cache_folder=settings.embedding_cache_folder,
            local_files_only=True,
        )

        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_function,
            configuration={
                "hnsw": {"space": "cosine"},
            },
        )
    except Exception as error:
        raise VectorStoreError(f"初始化 chroma 失败: {error}") from error


def sync_questions_to_chroma(db: Session) -> dict[str, int]:
    """把 SQLite 中的全部面试题同步到 Chroma"""

    question_models = db.scalars(
        select(InterviewQuestion).order_by(InterviewQuestion.id.asc())
    ).all()

    collection = get_question_collection()

    if not question_models:
        return {
            "indexed_count": 0,
            "collection_count": collection.count(),
        }

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []

    for question_model in question_models:
        question = to_question_public(question_model)

        ids.append(str(question.id))
        documents.append(build_question_document(question))
        metadatas.append(
            {
                "question_id": question.id,
                "difficulty": question.difficulty,
                "tags_json": json.dumps(
                    question.tags,
                    ensure_ascii=False,
                ),
            }
        )

    try:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
    except Exception as error:
        raise VectorStoreError(f"同步面试题向量失败: {error}") from error

    return {
        "indexed_count": len(ids),
        "collection_count": collection.count(),
    }


def search_questions_with_chroma(
    db: Session,
    request: QuestionVectorSearchRequest,
) -> list[QuestionVectorSearchItem]:
    """使用 Chroma 进行语义检索，再从 SQLite 获取完整题目"""

    collection = get_question_collection()
    collection_count = collection.count()

    if collection_count == 0:
        return []

    # 标签还需要在 Python 中二次筛选，所以适当多召回候选项
    candidate_count = min(collection_count, max(request.top_k * 5, request.top_k))

    query_arguments: dict[str, Any] = {
        "query_texts": [request.query],
        "n_results": candidate_count,
        "include": ["metadatas", "distances"],
    }

    if request.difficulty is not None:
        query_arguments["where"] = {"difficulty": request.difficulty}

    try:
        raw_result = collection.query(**query_arguments)
    except Exception as error:
        raise VectorStoreError(f"Chroma 检索失败: {error}") from error

    nested_ids = raw_result.get("ids")
    nested_distances = raw_result.get("distances")

    if not nested_ids or not nested_ids[0]:
        return []

    if not nested_distances or not nested_distances[0]:
        raise VectorStoreError("Chroma 返回结果缺少 distances")

    chroma_ids = nested_ids[0]
    distances = nested_distances[0]

    if len(chroma_ids) != len(distances):
        raise VectorStoreError("Chroma 返回的 Id 与距离数量不一致")

    try:
        question_ids = [int(chroma_id) for chroma_id in chroma_ids]
    except ValueError as error:
        raise VectorStoreError("Chroma 中存在非法题目 ID") from error

    question_models = db.scalars(
        select(InterviewQuestion).where(InterviewQuestion.id.in_(question_ids))
    ).all()

    question_map = {question.id: question for question in question_models}
    required_tags = {tag.casefold() for tag in request.tags}
    results: list[QuestionVectorSearchItem] = []

    for question_id, distance in zip(question_ids, distances):
        question_model = question_map.get(question_id)

        if question_model is None:
            continue

        question = to_question_public(question_model)
        question_tags = {tag.casefold() for tag in question.tags}
        
        if not required_tags.issubset(question_tags):
            continue
        
        # Collection 使用 cosine 空间时:
        # distance = 1 - cosine_similarity
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))

        if similarity < request.min_similarity:
            continue

        results.append(
            QuestionVectorSearchItem(question=question, similarity=similarity)
        )

        if len(results) >= request.top_k:
            break

    return results


def upsert_question_to_chroma(
    question: InterviewQuestionPublic,
) -> None:
    """将单道面试题新增或更新到 Chroma"""

    collection = get_question_collection()

    question_id = str(question.id)
    document = build_question_document(question)

    metadata: dict[str, str | int] = {
        "question_id": question.id,
        "difficulty": question.difficulty,
        "tags_json": json.dumps(
            question.tags,
            ensure_ascii=False,
        ),
    }

    try:
        collection.upsert(
            ids=[question_id],
            documents=[document],
            metadatas=[metadata],
        )
    except Exception as error:
        raise VectorStoreError(
            f"同步题目 {question.id} 到 Chroma 失败：{error}"
        ) from error
