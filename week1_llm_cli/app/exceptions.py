class LLMCLIError(Exception):
    """CLI 工具的业务异常基类。

    以后只要是“用户可以理解并修正”的错误，都可以继承这个类。
    """
    


class InputValidationError(LLMCLIError):
    """用户输入不合法，例如 message 为空。"""


class HistoryArgumentError(LLMCLIError):
    """历史记录相关参数不合法，例如 history_limit 为负数。"""


class ConfigError(LLMCLIError):
    """配置文件相关错误。"""


class LLMRequestError(LLMCLIError):
    """LLM 请求相关错误。"""