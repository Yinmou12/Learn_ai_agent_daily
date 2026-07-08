import unittest

from fastapi.testclient import TestClient

from app.main import app


class AuthRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_login_success(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "demo",
                "password": "123456",
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertIn("access_token", body["data"])
        self.assertEqual(body["data"]["token_type"], "bearer")
        self.assertIsNone(body["error"])

    def test_login_wrong_password_returns_401(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "demo",
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 401)

        body = response.json()
        self.assertEqual(body["success"], False)
        self.assertEqual(body["error"]["code"], "AuthError")

    def test_me_without_token_returns_401(self) -> None:
        response = self.client.get("/api/v1/auth/me")

        # HTTPBearer 在没有 Authorization 头时，默认返回 401。
        self.assertEqual(response.status_code, 401)

    def test_me_with_token_success(self) -> None:
        login_response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": "demo",
                "password": "123456",
            },
        )

        token = login_response.json()["data"]["access_token"]

        response = self.client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["data"]["username"], "demo")


if __name__ == "__main__":
    unittest.main()
