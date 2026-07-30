import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.schemas import (
    InterviewQuestionPublic,
    QuestionVectorSearchItem,
    RAGQuestionGenerateRequest,
)
from app.services.rag_question_service import (
    generate_rag_question_set,
)


class RAGQuestionServiceTest(unittest.TestCase):
    @patch("app.services.rag_question_service." "search_questions_with_chroma")
    def test_fake_generation_keeps_source_id(
        self,
        mock_search: Mock,
    ) -> None:
        source_question = InterviewQuestionPublic(
            id=10,
            question="FastAPI Depends 有什么作用？",
            reference_answer="用于声明依赖注入。",
            key_points=["依赖注入", "逻辑复用"],
            difficulty="medium",
            tags=["FastAPI", "Depends"],
            created_at=datetime.now(timezone.utc),
        )

        mock_search.return_value = [
            QuestionVectorSearchItem(
                similarity=0.82,
                question=source_question,
            )
        ]

        request = RAGQuestionGenerateRequest(
            query="FastAPI 依赖注入",
            tags=["FastAPI"],
            difficulty="medium",
            source_top_k=1,
            question_count=1,
            use_fake=True,
        )

        result = generate_rag_question_set(
            db=Mock(spec=Session),
            request=request,
        )

        self.assertEqual(len(result.questions), 1)
        self.assertEqual(
            result.questions[0].source_question_ids,
            [10],
        )
        self.assertEqual(result.sources[0].question_id, 10)


if __name__ == "__main__":
    unittest.main()
