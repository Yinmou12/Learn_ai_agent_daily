import json
from typing import Any

from pydantic import ValidationError
from app.clients.llm_client import call_llm
from app.config import load_settings
from app.exceptions import ResumeParseError
from app.schemas import ResumeProfile


def build_resume_parse_prompt(resume_text: str) -> str:
    """构造简历解析 Prompt"""

    return f"""
请从下面的简历文本中提取结构化信息。

要求：
1. 只返回 JSON，不要返回 Markdown。
2. 不要添加解释文字。
3. JSON 字段必须包含：
   - name: 字符串
   - skills: 字符串数组
   - years_of_experience: 整数
   - target_roles: 字符串数组
   - summary: 字符串

简历文本：
{resume_text}
""".strip()


def parse_resume_json(raw_text: str) -> ResumeProfile:
    """
    把大模型返回的 JSON 文本解析成 ResumeProfile
    """

    try:
        data: dict[str, Any] = json.loads(raw_text)
    except json.JSONDecodeError as error:
        raise ResumeParseError("大模型返回的内容不是合法 JSON") from error

    try:
        return ResumeProfile.model_validate(data)
    except ValidationError as error:
        raise ResumeParseError(f"简历结构化字段校验失败:{error}") from error


def fake_parse_resume(resume_text: str) -> ResumeProfile:
    """假解析结果，用于本地调试。"""

    return ResumeProfile(
        name="示例候选人",
        skills=["Python", "FastAPI", "SQLAlchemy", "LLM API"],
        years_of_experience=1,
        target_roles=["Python 后端实习生", "AI Agent 实习生"],
        summary="具备 Python 后端基础，正在构建 AI Agent 方向项目。",
    )


def parse_resume(resume_text: str, use_fake: bool = True) -> ResumeProfile:
    """
    解析简历文本
    """

    if use_fake:
        return fake_parse_resume(resume_text)

    settings = load_settings()
    prompt = build_resume_parse_prompt(resume_text)
    raw_answer = call_llm(settings=settings, user_text=prompt)

    return parse_resume_json(raw_answer)
