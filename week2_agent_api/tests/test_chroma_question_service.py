import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion
from app.services.chroma_question_service import (
    sync_questions_to_chroma,
)


class ChromaQuestionServiceTest(unittest.TestCase):
    @patch("app.services.chroma_question_service." "get_question_collection")
    def test_sync_questions_uses_database_id(
        self,
        mock_get_collection: Mock,
    ) -> None:
        question = InterviewQuestion(
            question="FastAPI Depends 有什么作用？",
            reference_answer="用于声明和解析依赖。",
            key_points_json='["依赖注入"]',
            difficulty="medium",
            tags_json='["FastAPI", "Depends"]',
        )
        question.id = 123
        question.created_at = datetime.now(timezone.utc)

        db = Mock(spec=Session)
        db.scalars.return_value.all.return_value = [question]

        collection = Mock()
        collection.count.return_value = 1
        mock_get_collection.return_value = collection

        result = sync_questions_to_chroma(db=db)

        self.assertEqual(result["indexed_count"], 1)

        upsert_arguments = collection.upsert.call_args.kwargs

        # Chroma ID 必须与数据库题目 ID 保持一致
        self.assertEqual(upsert_arguments["ids"], ["123"])
        self.assertEqual(
            upsert_arguments["metadatas"][0]["question_id"],
            123,
        )


if __name__ == "__main__":
    unittest.main()
