from typing import Any
from pydantic import BaseModel, Field, field_validator


class ErrorDetail(BaseModel):
    """
    统一错误信息结构

    code 给程序看，message 给用户看。
    例如前端可以根据 code 判断应该弹出什么提示。
    """

    code: str = Field(description="错误代码")
    message: str = Field(description="错误说明")


class ApiResponse(BaseModel):
    """
    统一响应结构

    success 表示接口是否成功。
    data 放成功数据，error 放失败信息。

    这里 data 暂时用 Any，是为了降低初学阶段的泛型复杂度。
    后面熟悉 Pydantic 后，可以再改成泛型模型。
    """

    success: bool = Field(description="接口是否成功")
    data: Any | None = Field(default=None, description="成功时返回的数据")
    error: ErrorDetail | None = Field(default=None, description="失败是返回的错误")
    request_id: str | None = Field(default=None, description="请求ID")


class HealthResponse(BaseModel):
    """
    健康检查接口的响应模型。

    BaseModel 来自 Pydantic。
    你可以把它理解成：用 Python 类定义 JSON 的结构。
    """

    status: str = Field(description="服务状态")
    service: str = Field(description="服务名称")


class VersionData(BaseModel):
    """本接口返回的数据内容。"""

    version: str = Field(description="当前服务版本")


class ChatRequest(BaseModel):
    """
    聊天接口的请求模型。

    message 是用户输入给后端的问题。
    min_length 和 max_length 是第一层校验。
    field_validator 是第二层业务校验。
    """

    message: str = Field(
        min_length=1,
        max_length=500,
        description="用户输入的问题，长度为 1 到 500 个字符",
        examples=["用三句话解释 FastAPI 路由是什么"],
    )

    use_fake: bool = Field(
        default=False,
        description="是否使用假回答，True 表示不调用真实大模型",
    )

    # 先检查 message 的类型、长度等基础规则
    @field_validator("message")
    @classmethod
    def validation_message_not_blank(cls, value: str) -> str:
        """
        校验 message 不能只是空格。

        注意：
        min_length=1 只能拦住空字符串。
        但 "   " 的长度是3，所以必须手动 strip 后再判断。
        """

        message = value.strip()
        if not message:
            raise ValueError("message 不能为空")

        return message


class ChatResponse(BaseModel):
    """
    聊天接口的响应模型。

    今天先返回模拟回答。明天再把这里接到真实 LLMClient
    """

    message: str = Field(description="用户问题")
    answer: str = Field(description="后端生成的回答")
    model: str = Field(description="当前使用的模型名称")


class DebugPing(BaseModel):
    """
    debug ping 接口返回的数据内容
    """

    message: str = Field(description="调试接口返回消息")
