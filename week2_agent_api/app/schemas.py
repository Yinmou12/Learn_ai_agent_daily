from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """
    健康检查接口的响应模型。

    BaseModel 来自 Pydantic。
    你可以把它理解成：用 Python 类定义 JSON 的结构。
    """
    status:str=Field(description="服务状态")
    service:str=Field(description="服务名称")


class ChatRequest(BaseModel):
    """
    聊天接口的请求模型。
    
    用户请求 POST /api/v1/chat 时，请求体应该长这样：
    {
        "message": "解释 FastAPI"
    }
    """

    message:str=Field(
        min_length=1,
        description="用户输入的问题，不能为空"
    )


class ChatResponse(BaseModel):
    """
    聊天接口的响应模型。

    今天先返回模拟回答。明天再把这里接到真实 LLMClient
    """

    message:str=Field(description="用户问题")
    answer:str=Field(description="后端返回的回答")
    model:str=Field(description="使用的模型名称")