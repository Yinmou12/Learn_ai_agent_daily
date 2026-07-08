from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import load_settings
from app.db.base import Base

settings = load_settings()
DATABASE_URL = settings.database_url


def ensure_sqlite_parent_dir(database_url: str) -> None:
    """
    确保 SQLite 文件所在目录存在
    """

    if not database_url.startswith("sqlite:///"):
        return

    db_path_text = database_url.replace("sqlite:///", "", 1)

    # 内存数据库 sqlite:///:memory: 不需要创建目录
    if db_path_text == ":memory":
        return

    db_path = Path(db_path_text)
    db_path.parent.mkdir(parents=True, exist_ok=True)


ensure_sqlite_parent_dir(DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def init_db() -> None:
    """
    创建数据库表

    注意：这只是学习阶段的简化做法。
    真实项目通常使用 Alembic 做数据库迁移。
    """

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    为每个请求创建一个数据库 Session

    yield 前：创建 Session
    yield 后：请求关闭，关闭 Session
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
