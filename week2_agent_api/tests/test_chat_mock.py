import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class ChatMockTest(unittest.TestCase):
    """演示如何 mock 服务层函数。"""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def get_token(self) -> str:
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "demo",
                "password": "123456",
            },
        )

        return response.json()["data"]["access_token"]

    @patch("app.api.routes.chat.generate_chat_answer")
    def test_chat_uses_mocked_service(self, mock_generate_chat_answer) -> None:
        """把路由中使用的 generate_chat_answer 临时替换成假函数。"""

        token = self.get_token()

        mock_generate_chat_answer.return_value = ("mock answer", "mock-model")

        response = self.client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "测试 mock",
                "use_fake": False,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["data"]["answer"], "mock answer")
        self.assertEqual(data["data"]["model"], "mock-model")

        mock_generate_chat_answer.assert_called_once_with(
            message="测试 mock",
            use_fake=False,
        )


if __name__ == "__main__":
    unittest.main()
