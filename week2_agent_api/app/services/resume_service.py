import json
from typing import Any

from sqlalchemy import select, func

from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.clients.llm_client import call_llm
from app.config import load_settings
from app.exceptions import ResumeParseError
from app.models.job_match_records import JobMatchRecord
from app.models.resume import ResumeRecord
from app.schemas import ResumeProfile, ResumeRecordPublic, JobMatchResult


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


def get_owned_resume_record(
    db: Session, user_id: int, resume_id: int
) -> ResumeRecordPublic:
    if not user_id:
        raise ValueError("user_id 和 resume_id 不能都为空")

    statement = select(ResumeRecord).where(
        ResumeRecord.user_id == user_id,
        ResumeRecord.id == resume_id,
    )

    record = db.scalar(statement)

    if record is None:
        raise ValueError("简历记录不存在")

    return record


def load_resume_profile(record: ResumeRecord) -> ResumeProfile:
    """
    把数据库里的 profile_json 还原成 ResumeProfile

    数据库存的是 JSON 字符串
    业务代码更适合使用 Pydantic 对象
    """

    try:
        data = json.loads(record.profile_json)
    except json.JSONDecodeError as error:
        raise ResumeParseError("数据库中的简历结构化结果不是合法 JSON") from error

    return ResumeProfile.model_validate(data)


def match_resume_with_jd(
    db: Session,
    user_id: int,
    resume_id: int,
    jd_text: str,
) -> JobMatchResult:
    """
    用规则匹配方式计算简历和 JD 的匹配度

    第一版不调用大模型，先保证结果稳定、可测试
    """

    record = get_owned_resume_record(
        db=db,
        user_id=user_id,
        resume_id=resume_id,
    )

    profile = load_resume_profile(record)

    jd_text_lower = jd_text.lower()

    matched_skills: list[str] = []
    missing_skills: list[str] = []

    for skill in profile.skills:
        skill_text = skill.strip()
        if not skill_text:
            continue

        # 用小写比较
        if skill_text.lower() in jd_text_lower:
            matched_skills.append(skill_text)
        else:
            missing_skills.append(skill_text)

    if profile.skills:
        score = int(len(matched_skills) / len(profile.skills) * 100)
    else:
        score = 0

    if score >= 80:
        suggestion = "匹配度较高，可以优先投递，并重点准备项目细节。"
        match_level = "high"
    elif score >= 50:
        suggestion = "匹配度中等，建议补充 JD 中高频出现但简历未体现的技能。"
        match_level = "medium"
    else:
        suggestion = "匹配度较低，建议先调整简历方向或选择更贴近当前技能栈的岗位。"
        match_level = "low"

    return JobMatchResult(
        resume_id=resume_id,
        score=score,
        match_level=match_level,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestion=suggestion,
    )


def save_job_match_result(
    db: Session,
    user_id: int,
    jd_text: str,
    result_json: JobMatchResult,
) -> JobMatchRecord:

    record = JobMatchRecord(
        user_id=user_id,
        resume_id=result_json.resume_id,
        job_description=jd_text,
        match_score=result_json.score,
        result_json=json.dumps(result_json.model_dump(), ensure_ascii=False),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
