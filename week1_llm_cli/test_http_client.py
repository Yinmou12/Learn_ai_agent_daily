import unittest

from app.http_client import call_echo_api, request_json


class HttpClientValidationTest(unittest.TestCase):
    def test_request_json_rejects_invalid_url(self) -> None:
        """URL 不以 http:// 或 https:// 开头时，应在发请求前直接报错。"""
        with self.assertRaises(ValueError) as context:
            request_json(method="GET", url="httpbin.org/get")

        self.assertIn("url 必须以 http:// 或 https:// 开头", str(context.exception))

    def test_call_echo_api_rejects_empty_message(self) -> None:
        """用户消息为空时，不应该继续发送 HTTP 请求。"""
        with self.assertRaises(ValueError) as context:
            call_echo_api("   ")

        self.assertIn("message 不能为空", str(context.exception))


if __name__ == "__main__":
    unittest.main()
