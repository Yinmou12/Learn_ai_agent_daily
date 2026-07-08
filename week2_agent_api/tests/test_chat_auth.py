import unittest

from fastapi.testclient import TestClient

from app.main import app


class ChatAuthTest(unittest.TestCase):
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

    def test_chat_without_token_returns_401(self) -> None:
        response = self.client.post(
            "/api/v1/chat",
            json={
                "message": "你好",
                "use_fake": True,
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_chat_with_token_success(self) -> None:
        token = self.get_token()

        response = self.client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "你好",
                "use_fake": True,
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["data"]["model"], "fake-llm")


if __name__ == "__main__":
    unittest.main()
