from typing import Any
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class JobMatchRecord(Base):

    __tablename__ = "job_match_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        index=True,
        nullable=False,
    )

    job_description: Mapped[str] = mapped_column(Text, nullable=False)

    match_score: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    result_json: Mapped[str] = mapped_column(Text, nullable=False)
