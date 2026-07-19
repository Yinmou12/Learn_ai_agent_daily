import time
import unittest

from fastapi.testclient import TestClient

from app.main import app


class QuestionsRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def register_and_login(self) -> str:
        username = f"question_user_{int(time.time() * 1000)}"

        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "123456",
                "display_name": "Question User",
            },
        )
        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": "123456",
            },
        )
        self.assertEqual(login_response.status_code, 200)

        return login_response.json()["data"]["access_token"]

    def test_create_question_success(self) -> None:
        token = self.register_and_login()
        unique_question = f"请解释测试题 {int(time.time() * 1000)}"

        response = self.client.post(
            "/api/v1/questions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question": unique_question,
                "reference_answer": "这是测试参考答案。",
                "key_points": ["测试点一", "测试点二"],
                "difficulty": "medium",
                "tags": ["Python", "TestOnly"],
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["question"], unique_question)
        self.assertEqual(body["data"]["difficulty"], "medium")
        self.assertIn("Python", body["data"]["tags"])

    def test_list_questions_filter_by_tag_and_difficulty(self) -> None:
        token = self.register_and_login()
        unique_tag = f"QuestionTag{int(time.time() * 1000)}"
        unique_question = f"筛选测试题 {unique_tag}"

        create_response = self.client.post(
            "/api/v1/questions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question": unique_question,
                "reference_answer": "用于测试 tag 和 difficulty 同时筛选。",
                "key_points": ["tag 筛选", "difficulty 筛选"],
                "difficulty": "hard",
                "tags": [unique_tag, "SQLAlchemy"],
            },
        )
        self.assertEqual(create_response.status_code, 200)

        list_response = self.client.get(
            f"/api/v1/questions?tag={unique_tag}&difficulty=hard",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(list_response.status_code, 200)

        body = list_response.json()
        self.assertTrue(body["success"])

        questions = body["data"]
        self.assertGreaterEqual(len(questions), 1)
        self.assertTrue(any(item["question"] == unique_question for item in questions))
        self.assertTrue(all(item["difficulty"] == "hard" for item in questions))
        self.assertTrue(all(unique_tag in item["tags"] for item in questions))

    def test_questions_require_login(self) -> None:
        response = self.client.get("/api/v1/questions")

        # 你的项目如果 HTTPBearer 默认未登录返回 403，就用 403
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
