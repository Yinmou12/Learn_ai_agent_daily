import unittest

from fastapi.testclient import TestClient

from app.main import app


class RouteTest(unittest.TestCase):
    """测试 FastAPI 路由。

    这些测试不需要启动 uvicorn。
    TestClient 会直接调用 FastAPI 应用。
    """

    def setUp(self) -> None:
        """每个测试执行前都会运行一次。"""
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

    def test_health_returns_ok(self) -> None:
        """健康检查接口应返回统一成功响应。"""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["data"]["status"], "ok")
        self.assertEqual(data["data"]["service"], "agent-backend-api")
        self.assertIsNone(data["error"])

    def test_version_returns_app_version(self) -> None:
        """版本接口应返回当前应用版本。"""
        response = self.client.get("/api/v1/version")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["data"]["version"], app.version)
        self.assertIsNone(data["error"])

    def test_debug_ping_returns_pong(self) -> None:
        """debug ping 接口应返回 pong。"""
        response = self.client.get("/api/v1/debug/ping")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["data"]["message"], "pong")
        self.assertIsNone(data["error"])

    def test_chat_with_fake_answer(self) -> None:
        """use_fake=True 时，不应调用真实大模型。"""
        token = self.get_token()
        response = self.client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "请解释 APIRouter",
                "use_fake": True,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["data"]["message"], "请解释 APIRouter")
        self.assertEqual(data["data"]["model"], "fake-llm")
        self.assertIn("请解释 APIRouter", data["data"]["answer"])
        self.assertIsNone(data["error"])

    def test_chat_rejects_blank_message(self) -> None:
        """全空格 message 应被 Pydantic validator 拦截。"""
        token = self.get_token()
        response = self.client.post(
            "/api/v1/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": "  ",
                "use_fake": True,
            },
        )

        # Pydantic 请求体验证失败时，FastAPI 默认返回 422。
        self.assertEqual(response.status_code, 422)

        data = response.json()
        self.assertIn("detail", data)


if __name__ == "__main__":
    unittest.main()
