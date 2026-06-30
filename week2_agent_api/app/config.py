from dataclasses import dataclass
from dotenv import load_dotenv
from functools import lru_cache

from app.exceptions import ConfigError

import os


@dataclass(frozen=True)
class Settings:
    """
    应用配置。

    frozen=True 表示创建后不建议修改。
    配置通常应该在启动或请求时读取，而不是在业务中随意改。
    """

    llm_api_key: str
    llm_base_url: str
    llm_model: str


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    """从 .env 读取配置并做基础校验。"""

    load_dotenv()

    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()

    missing_names: list[str] = []

    if not api_key:
        missing_names.append("LLM_API_KEY")

    if not base_url:
        missing_names.append("LLM_BASE_URL")

    if not model:
        missing_names.append("LLM_MODEL")

    if missing_names:
        raise ConfigError(f"缺少环境变量：{', '.join(missing_names)}")

    return Settings(
        llm_api_key=api_key,
        llm_base_url=base_url,
        llm_model=model,
    )
