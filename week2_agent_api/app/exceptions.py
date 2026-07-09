class AppError(Exception):
    """应用内可预期异常的基类。"""


class ConfigError(AppError):
    """配置缺失或配置不合法。"""


class LLMRequestError(AppError):
    """大模型请求失败。"""


class AuthError(AppError):
    """认证失败。例如用户名密码错误或 token 无效。"""


class NotFoundError(AppError):
    """资源不存在。例如通过id查询的用户不存在。"""


class ParameterError(Exception):
    """请求参数错误。"""
