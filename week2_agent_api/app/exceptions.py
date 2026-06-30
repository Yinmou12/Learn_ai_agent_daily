class AppError(Exception):
    """应用内可预期异常的基类。"""


class ConfigError(AppError):
    """配置缺失或配置不合法。"""


class LLMRequestError(AppError):
    """大模型请求失败。"""
