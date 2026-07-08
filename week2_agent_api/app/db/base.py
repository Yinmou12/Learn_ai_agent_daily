from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    所有 SQLAlchemy ORM 模型的基类

    后续 User, Resume, InterviewRecord 等模型都会继承它
    """
