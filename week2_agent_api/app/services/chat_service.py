from app.clients.llm_client import call_llm
from app.config import load_settings


def generate_chat_answer(message: str, use_fake: bool = False) -> tuple[str, str]:
    """
    根据 use_fake 决定使用假回答还是真实 LLM。

    返回值：
    - 第一个 str：回答内容
    - 第二个 str：模型名称
    """

    if use_fake:
        return generate_fake_answer(message), "fake-llm"

    return generate_llm_answer(message), "real-llm"


def generate_llm_answer(message: str) -> str:
    """
    生成真实 LLM 回答。

    服务层只关心“给我一个 message，我返回 answer”。
    它不关心 FastAPI 路由细节，也不直接构造 ApiResponse。
    """

    settings = load_settings()

    return call_llm(settings, message)


def generate_fake_answer(message: str) -> str:
    """
    生成临时假回答。

    这个函数是为了隔离业务逻辑。
    明天接入真实 LLM 时，优先替换这里，而不是改路由函数整体结构。
    保留假回答函数，方便本地调试。
    """

    return f"我收到了你的问题: {message}"
