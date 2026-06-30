from fastapi import APIRouter

from app.schemas import ApiResponse, ChatResponse, ChatRequest
from app.services.chat_service import generate_chat_answer
from app.utils.response import make_success_response

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ApiResponse)
def chat(request: ChatRequest) -> ApiResponse:
    """
    聊天接口。

    注意：这里不再写 try/except AppError。
    如果服务层抛出 AppError，会由全局异常处理器统一接管。
    """

    answer, model_name = generate_chat_answer(
        message=request.message, use_fake=request.use_fake
    )

    data = ChatResponse(
        message=request.message,
        answer=answer,
        model=model_name,
    )

    return make_success_response(data)
