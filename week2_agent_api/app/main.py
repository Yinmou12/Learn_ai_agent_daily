from fastapi import FastAPI

from app.exceptions import AppError
from app.schemas import (
    ErrorDetail,
    ApiResponse,
    HealthResponse,
    VersionData,
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import generate_chat_answer
from app.utils.response import make_success_response, make_error_response

app = FastAPI(
    title="Agent Backend API",
    description="Week2 最小 Agent 后端服务骨架",
    version="0.2.0",
)


@app.get("/health", response_model=ApiResponse)
def health_check() -> ApiResponse:
    """
    健康检查接口

    这个接口用于确认服务是否正常启动。
    一般不会写复杂业务逻辑，只返回服务状态。
    """

    data = HealthResponse(status="ok", service="agent-backend-api")
    return make_success_response(data)


@app.get("/api/v1/version", response_model=ApiResponse)
def get_version() -> ApiResponse:
    """查询服务版本号。"""

    data = VersionData(version=app.version)
    return make_success_response(data)


@app.post("/api/v1/chat", response_model=ApiResponse)
def chat(request: ChatRequest) -> ApiResponse:
    """
    聊天接口

    路由函数只做三件事：
    1. 接收已经通过 Pydantic 校验的 request。
    2. 调用服务层生成 answer。
    3. 返回统一响应。
    """

    try:
        answer, model_name = generate_chat_answer(request.message, request.use_fake)

        data = ChatResponse(
            message=request.message,
            answer=answer,
            model=model_name,
        )
        return make_success_response(data)
    except AppError as error:
        return make_error_response(code=error.__class__.__name__, message=str(error))


@app.post("/api/v1/chat/debug", response_model=ApiResponse)
def chat_debug(request: ChatRequest) -> ApiResponse:
    """
    聊天接口测试

    返回用户输入的长度和清洗后的内容
    """
    try:
        message_length = len(request.message)
        cleaned_message = request.message.strip()  # 简单清洗示例

        data = {
            "original_message": request.message,
            "message_length": message_length,
            "cleaned_message": cleaned_message,
            "cleaned_message_length": len(cleaned_message),
        }

        return make_success_response(data)
    except AppError as error:
        return make_error_response(code=error.__class__.__name__, message=str(error))
