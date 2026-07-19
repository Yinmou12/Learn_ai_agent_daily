import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interview_question import InterviewQuestion

SEED_INTERVIEW_QUESTIONS: list[dict[str, object]] = [
    {
        "question": "请解释 Python 中 list 和 tuple 的区别。",
        "reference_answer": "list 是可变序列，tuple 是不可变序列。list 适合需要增删改的场景，tuple 适合表达固定结构的数据。",
        "key_points": ["可变与不可变", "使用场景", "序列类型"],
        "difficulty": "easy",
        "tags": ["Python"],
    },
    {
        "question": "请解释 Python 中装饰器的作用。",
        "reference_answer": "装饰器用于在不修改原函数代码的前提下增强函数行为，常见于日志、权限校验、缓存和路由注册。",
        "key_points": ["函数也是对象", "增强函数行为", "不修改原函数"],
        "difficulty": "medium",
        "tags": ["Python", "装饰器"],
    },
    {
        "question": "FastAPI 中 Depends 的作用是什么？",
        "reference_answer": "Depends 用于声明依赖注入，让路由函数自动获取数据库 Session、当前用户、配置对象等公共依赖。",
        "key_points": ["依赖注入", "复用公共逻辑", "认证", "数据库 Session"],
        "difficulty": "medium",
        "tags": ["FastAPI", "Depends"],
    },
    {
        "question": "FastAPI 中为什么要使用 Pydantic Schema？",
        "reference_answer": "Pydantic Schema 用于定义请求和响应的数据结构，并在请求进入业务逻辑前完成类型校验和业务校验。",
        "key_points": ["请求校验", "响应结构", "类型约束", "业务校验"],
        "difficulty": "easy",
        "tags": ["FastAPI", "Pydantic"],
    },
    {
        "question": "SQLAlchemy 中 Session 的作用是什么？",
        "reference_answer": "Session 是应用代码和数据库之间的工作单元，负责查询、添加、提交、回滚和刷新 ORM 对象。",
        "key_points": ["工作单元", "db.add", "db.commit", "db.refresh", "事务"],
        "difficulty": "medium",
        "tags": ["SQLAlchemy", "数据库"],
    },
]


def seed_interview_questions(db: Session) -> None:
    """
    初始化面试题种子数据。

    通过 question 字段判断是否已存在，避免每次启动服务都重复插入。
    """

    for item in SEED_INTERVIEW_QUESTIONS:
        question_text = str(item["question"])

        existing = db.scalar(
            select(InterviewQuestion).where(InterviewQuestion.question == question_text)
        )

        if existing is not None:
            continue

        question = InterviewQuestion(
            question=question_text,
            reference_answer=str(item["reference_answer"]),
            key_points_json=json.dumps(item["key_points"], ensure_ascii=False),
            difficulty=str(item["difficulty"]),
            tags_json=json.dumps(item["tags"], ensure_ascii=False),
        )

        db.add(question)

    db.commit()
