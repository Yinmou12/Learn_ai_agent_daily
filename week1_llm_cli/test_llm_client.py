import unittest

from app.exceptions import LLMRequestError
from app.llm_client import parse_assistant_message


class LLMClientTest(unittest.TestCase):
    """只测试响应解析，不测试真实 API 请求。"""

    def test_parse_assistant_message_success(self) -> None:
        """标准响应结构应能解析出 assistant 内容。"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "这是模型回复。"
                    }
                }
            ]
        }

        result = parse_assistant_message(response_data)

        self.assertEqual(result, "这是模型回复。")

    def test_parse_assistant_message_rejects_missing_choices(self) -> None:
        """响应缺少 choices 时，应抛出明确异常。"""
        with self.assertRaises(LLMRequestError):
            parse_assistant_message({})

    def test_parse_assistant_message_rejects_empty_content(self) -> None:
        """模型返回空内容时，应抛出明确异常。"""
        response_data = {
            "choices": [
                {
                    "message": {
                        "content": "   "
                    }
                }
            ]
        }

        with self.assertRaises(LLMRequestError):
            parse_assistant_message(response_data)


if __name__ == "__main__":
    unittest.main()