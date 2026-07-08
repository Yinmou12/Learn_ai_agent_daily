from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions import AuthError
from app.models.user import User
from app.schemas import UserCreate, UserProfile
from app.security.password import hash_password, verify_password


def get_user_model_by_username(db: Session, username: str) -> User | None:
    """
    根据 username 查询用户 ORM 对象
    """

    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def create_user(db: Session, user_create: UserCreate) -> UserProfile:
    """
    创建用户
    """

    existing_user = get_user_model_by_username(
        db=db,
        username=user_create.username,
    )

    if existing_user is not None:
        raise AuthError("用户名已存在")

    user = User(
        username=user_create.username,
        password_hash=hash_password(user_create.password),
        display_name=user_create.display_name,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserProfile(
        username=user.username,
        display_name=user.display_name,
    )


def authenticate_user(db: Session, username: str, password: str) -> UserProfile:
    """
    从数据库校验用户名和密码
    """

    user = get_user_model_by_username(
        db=db,
        username=username,
    )

    if user is None:
        raise AuthError("用户名错误")

    if not verify_password(password, user.password_hash):
        raise AuthError("密码错误")

    return UserProfile(
        username=user.username,
        display_name=user.display_name,
    )


def get_user_by_username(db: Session, username: str) -> UserProfile:
    """
    根据 username 获取当前用户信息
    """

    user = get_user_model_by_username(
        db=db,
        username=username,
    )

    if user is None:
        raise AuthError("用户不存在")

    return UserProfile(
        username=user.username,
        display_name=user.display_name,
    )
