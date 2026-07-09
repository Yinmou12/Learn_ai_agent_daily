import time
import unittest

from fastapi.testclient import TestClient

from app.main import app


class UsersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def register_and_login(self) -> str:
        username = f"list_user_{int(time.time()*10000)}"

        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "123456",
                "display_name": "List User",
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

    def test_list_users_requires_login(self) -> None:
        response = self.client.get("/api/v1/users")

        self.assertEqual(response.status_code, 401)

    def test_list_users_success(self) -> None:
        token = self.register_and_login()

        response = self.client.get(
            "/api/v1/users?page=1&page_size=10",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["success"], True)
        self.assertIn("items", body["data"])
        self.assertIn("total", body["data"])
        self.assertEqual(body["data"]["page"], 1)
        self.assertEqual(body["data"]["page_size"], 10)

    def test_list_users_rejects_invalid_page(self) -> None:
        token = self.register_and_login()

        response = self.client.get(
            "/api/v1/users?page=0&page_size=10",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
