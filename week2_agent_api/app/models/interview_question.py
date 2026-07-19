from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InterviewQuestion(Base):

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    question: Mapped[str] = mapped_column(Text, nullable=False)

    reference_answer: Mapped[str] = mapped_column(Text, nullable=False)

    # 评分关键点,第一版先用 JSON 字符串保存
    key_points_json: Mapped[str] = mapped_column(Text, nullable=False)

    difficulty: Mapped[str] = mapped_column(Text, nullable=False)

    # 技能标签,例如 ["Python", "FastAPI", "SQLAlchemy"]
    tags_json: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
