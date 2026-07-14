import json
from typing import Any

from sqlalchemy import select, func

from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.clients.llm_client import call_llm
from app.config import load_settings
from app.exceptions import ResumeParseError
from app.models.resume import ResumeRecord
from app.schemas import ResumeProfile, ResumeRecordPublic


def to_resume_record_public(resume_record: ResumeRecord) -> ResumeRecordPublic:
    return ResumeRecordPublic(
        id=resume_record.id,
        raw_text=resume_record.raw_text,
        created_at=resume_record.created_at,
        updated_at=resume_record.updated_at,
    )


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


def save_resume_profile(
    db: Session,
    user_id: int,
    raw_text: str,
    profile: ResumeProfile,
) -> ResumeRecord:
    if not raw_text:
        raise ValueError("raw_text 不能为空")

    record = ResumeRecord(
        user_id=user_id,
        raw_text=raw_text,
        # model_dump() 把 Pydantic 对象转成 dict
        # ensure_ascii=False 保证中文不会变成 Unicode 转义
        profile_json=json.dumps(profile.model_dump(), ensure_ascii=False),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def list_current_user_resume_records(db: Session, user_id) -> list[ResumeRecordPublic]:

    statement = (
        select(ResumeRecord)
        .where(ResumeRecord.user_id == user_id)
        .order_by(ResumeRecord.id.desc())
    )

    resumes = db.scalars(statement).all()

    return [to_resume_record_public(resume) for resume in resumes]


def search_resume_record_by_id(db: Session, user_id: int) -> ResumeRecordPublic:
    if not user_id:
        raise ValueError("user_id 和 resume_id 不能都为空")

    statement = select(ResumeRecord).where(
        ResumeRecord.user_id == user_id,
    )

    record = db.scalar(statement)

    if record is None:
        raise ValueError("简历记录不存在")

    return to_resume_record_public(record)
