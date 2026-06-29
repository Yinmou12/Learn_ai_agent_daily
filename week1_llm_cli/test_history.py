import tempfile
import unittest
from pathlib import Path

from app.history import append_message, load_history, save_history

Message = dict[str, str]


class HistoryTest(unittest.TestCase):
    """测试历史记录 JSON 读写逻辑。"""

    def test_load_history_returns_empty_list_when_file_missing(self) -> None:
        """历史文件不存在时，应返回空列表，而不是报错。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"

            result = load_history(history_path)

            self.assertEqual(result, [])

    def test_save_and_load_history(self) -> None:
        """保存后再次读取，应拿到相同消息。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            messages: list[Message] = [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "你好，我可以帮你学习 AI Agent。"},
            ]

            save_history(messages, history_path)
            result = load_history(history_path)

            self.assertEqual(result, messages)

    def test_append_message_adds_one_message(self) -> None:
        """append_message 应在原有历史末尾追加一条消息。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"

            append_message({"role": "user", "content": "第一条"}, history_path)
            append_message({"role": "assistant", "content": "第二条"}, history_path)

            result = load_history(history_path)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["role"], "user")
            self.assertEqual(result[1]["role"], "assistant")

    def test_load_history_returns_empty_list_when_file_is_empty(self) -> None:
        """历史文件存在但内容为空时，应返回空列表。

        这是你之前修过的 Bug，今天要用测试固定下来。
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text("", encoding="utf-8")

            result = load_history(history_path)

            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()