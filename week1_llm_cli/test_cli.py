import unittest

from app.cli import normalize_message, validate_history_limit
from app.exceptions import HistoryArgumentError, InputValidationError


class CLITest(unittest.TestCase):
    """测试 CLI 输入校验逻辑。

    这些测试不依赖网络、不依赖 API Key，应该稳定通过。
    """

    def test_normalize_message_rejects_none(self) -> None:
        """没有传入 --message 时，应主动报错。"""
        with self.assertRaises(InputValidationError):
            normalize_message(None)

    def test_normalize_message_rejects_blank_text(self) -> None:
        """只输入空格时，应主动报错。"""
        with self.assertRaises(InputValidationError):
            normalize_message("   ")

    def test_normalize_message_strips_text(self) -> None:
        """首尾空格应该被清理，避免保存脏数据。"""
        result = normalize_message("  你好  ")
        self.assertEqual(result, "你好")

    def test_validate_history_limit_rejects_negative_number(self) -> None:
        """history-limit 不能为负数。"""
        with self.assertRaises(HistoryArgumentError):
            validate_history_limit(-1)

    def test_validate_history_limit_accepts_zero(self) -> None:
        """0 表示不主动展示历史，是合法值。"""
        validate_history_limit(0)

    def test_validate_history_limit_accepts_positive_number(self) -> None:
        """正数表示展示最近 N 条历史，是合法值。"""
        validate_history_limit(5)


if __name__ == "__main__":
    unittest.main()