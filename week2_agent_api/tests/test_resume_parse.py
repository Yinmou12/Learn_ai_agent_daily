import time
import unittest

from fastapi.testclient import TestClient

from app.main import app


class ResumeParseTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def register_and_login(self) -> str:
        username = f"resume_user_{int(time.time() * 1000)}"
        password = "test_password_123"

        register_response = self.client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": password,
                "display_name": "Resume Test User",
            },
        )
        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": password,
            },
        )
        self.assertEqual(login_response.status_code, 200)

        body = login_response.json()
        return body["data"]["access_token"]

    def test_parse_resume_with_fake_success(self):
        token = self.register_and_login()

        response = self.client.post(
            "/api/v1/resumes/parse",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "resume_text": "张三，熟悉 Python、FastAPI、SQLAlchemy，有 1 年项目经验。",
                "use_fake": True,
            },
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertTrue(body["success"])
        self.assertIn("data", body)

        data = body["data"]
        self.assertIn("name", data)
        self.assertIn("skills", data)
        self.assertIn("years_of_experience", data)
        self.assertIn("target_roles", data)
        self.assertIn("summary", data)

        self.assertIsInstance(data["skills"], list)
        self.assertGreater(len(data["skills"]), 0)

    def test_parse_resume_requires_login(self):
        response = self.client.post(
            "/api/v1/resumes/parse",
            json={
                "resume_text": "张三，熟悉 Python。",
                "use_fake": True,
            },
        )

        self.assertIn(response.status_code, [401, 403])

    def test_parse_resume_rejects_blank_text(self):
        token = self.register_and_login()

        response = self.client.post(
            "/api/v1/resumes/parse",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "resume_text": "   ",
                "use_fake": True,
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
