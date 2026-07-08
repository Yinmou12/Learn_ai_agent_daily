import time
import unittest

from fastapi.testclient import TestClient

from app.main import app


class UsersRouteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def register_and_login(self) -> tuple[str, str]:
        username = f"user_me_{int(time.time() * 1000)}"

        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "123456",
                "display_name": "User Me",
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

        token = login_response.json()["data"]["access_token"]

        return username, token

    def test_users_me_success(self) -> None:
        username, token = self.register_and_login()

        response = self.client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertEqual(body["data"]["username"], username)
        self.assertEqual(body["data"]["display_name"], "User Me")

    def test_users_me_without_token_returns_403(self) -> None:
        response = self.client.get("/api/v1/users/me")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
