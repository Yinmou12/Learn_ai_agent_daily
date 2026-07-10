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

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_minutes: int

    database_url: str

    log_level: str


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    """从 .env 读取配置并做基础校验。"""

    load_dotenv()

    jwt_expire_minutes_text = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60").strip()

    try:
        jwt_expire_minutes = int(jwt_expire_minutes_text)
    except ValueError as error:
        raise ConfigError("JWT_EXPIRE_MINUTES 必须是整数") from error

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    allowed_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
    if log_level not in allowed_log_levels:
        raise ConfigError("LOG_LEVLL 只能是 DEBUG、INFO、、WARNING、ERROR")

    settings = Settings(
        llm_api_key=os.getenv("LLM_API_KEY", "").strip(),
        llm_base_url=os.getenv("LLM_BASE_URL", "").strip(),
        llm_model=os.getenv("LLM_MODEL", "").strip(),
        jwt_secret_key=os.getenv("SECRET_KEY", "").strip(),
        jwt_algorithm=os.getenv("ALGORITHM", "HS256").strip(),
        jwt_expire_minutes=jwt_expire_minutes,
        database_url=os.getenv("DATABASE_URL", "sqlite:///data/app.db").strip(),
        log_level=log_level,
    )

    missing_names: list[str] = []

    if not settings.llm_api_key:
        missing_names.append("LLM_API_KEY")

    if not settings.llm_base_url:
        missing_names.append("LLM_BASE_URL")

    if not settings.llm_model:
        missing_names.append("LLM_MODEL")

    if not settings.jwt_secret_key:
        missing_names.append("SECRET_KEY")

    if not settings.jwt_algorithm:
        missing_names.append("ALGORITHM")

    if not settings.database_url:
        missing_names.append("DATABASE_URL")

    if missing_names:
        raise ConfigError(f"缺少环境变量：{', '.join(missing_names)}")

    return settings
