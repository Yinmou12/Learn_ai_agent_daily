from fastapi import FastAPI, HTTPException
from app.schemas import ChatRequest, ChatResponse, HealthResponse

app=FastAPI(
    title="Agent Backend API",
    description="Week2 最小 Agent 后端服务骨架",
    version="0.1.0",
)

@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    健康检查接口

    这个接口用于确认服务是否正常启动。
    一般不会写复杂业务逻辑，只返回服务状态。
    """

    return HealthResponse(status="ok", service="agent-backend-api")


def generate_fake_answer(message: str)->str:
    # 虽然 Pydantic 已经限制了 min_length=1,
    # 但用户可能传入 "   " 这种全空字符串，所以这里再做一次业务校验。
    if not message:
        raise HTTPException(
            status_code=400,
            detail="message 不能为空"
        )

    return f"我收到了你的问题: {message}"


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    聊天接口

    request 是 FastAPI 根据请求体自动创建出来的对象。
    如果请求不符合 ChatRequest 的要求，FastAPI 会自动返回 422 错误。
    """

    user_message = request.message.strip()

    # 今天先返回模拟回复，目的是先打通 HTTP 接口流程。
    # 明天可以把这行替换成真实的大模型调用。
    fake_answer=generate_fake_answer(user_message)

    return ChatResponse(
        message=user_message,
        answer=fake_answer,
        model="fake-llm"
    )


@app.get("/api/v1/version")
def get_version() -> dict:
    return {"version": app.version}