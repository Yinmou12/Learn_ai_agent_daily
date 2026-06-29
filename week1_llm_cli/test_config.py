import unittest

from app.exceptions import ConfigError
from app.config import load_settings


class ConfigTest(unittest.TestCase):
    def test_load_settings_success(self) -> None:
        """测试成功加载配置。"""
        settings = load_settings()
        self.assertIsInstance(settings, object)
        self.assertTrue(settings.api_key)
        self.assertTrue(settings.base_url)
        self.assertTrue(settings.model)

    def test_load_settings_missing_env_file(self) -> None:
        """测试缺少 .env 文件时抛出异常。"""
        # Temporarily rename the .env file to simulate missing file
        env_path = load_settings.__globals__['ENV_PATH']
        temp_env_path = env_path.with_suffix('.env.temp')
        if env_path.exists():
            env_path.rename(temp_env_path)

        try:
            with self.assertRaises(ConfigError):
                load_settings()
        finally:
            # Restore the .env file
            if temp_env_path.exists():
                temp_env_path.rename(env_path)