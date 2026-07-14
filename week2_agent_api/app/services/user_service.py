from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.exceptions import AuthError, NotFoundError, ParameterError
from app.models.user import User
from app.schemas import UserCreate, UserProfile, UserPublic, UserListData
from app.security.password import hash_password, verify_password


def to_user_public(user: User) -> UserPublic:
    """把 ORM User 对象转换成对外安全返回的 UserPublic。"""

    return UserPublic(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        created_at=user.created_at,
    )


def get_user_model_by_username(db: Session, username: str) -> User | None:
    """
    根据 username 查询用户 ORM 对象
    """

    if username is None:
        raise ParameterError("用户名不能为空")

    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_user_model_by_id(db: Session, user_id: int) -> User | None:
    """
    根据 user_id 查询用户 ORM 对象
    """

    if user_id is None:
        raise ParameterError("用户 ID 不能为空")

    statement = select(User).where(User.id == user_id)
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
        id=user.id,
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
        id=user.id,
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
        id=user.id,
        username=user.username,
        display_name=user.display_name,
    )


def count_users(db: Session) -> int:
    """统计总用户数"""

    statement = select(func.count()).select_from(User)
    return db.scalar(statement) or 0


def list_users(db: Session, page: int, page_size: int) -> UserListData:
    """
    分页查询用户列表
    """

    offset = (page - 1) * page_size

    statement = select(User).order_by(User.id.desc()).offset(offset).limit(page_size)

    users = db.scalars(statement).all()

    return UserListData(
        items=[to_user_public(user) for user in users],
        total=count_users(db),
        page=page,
        page_size=page_size,
    )


def get_user_info(db: Session, username: str, user_id: int) -> UserPublic:
    """
    查询单个用户
    """
    if username is None and user_id is None:
        raise ParameterError("用户名和 ID 不能都为空")

    user = None
    # 优先根据 用户名 搜素
    if (username and user_id) or username:
        user = get_user_model_by_username(db, username)
    elif user_id:
        user = get_user_model_by_id(db, user_id)

    if user is None:
        raise NotFoundError("用户不存在")

    return to_user_public(user)


def update_user_display_name(
    db: Session, username: str, display_name: str
) -> UserProfile:
    """
    更新用户展示名称
    """

    statement = select(User).where(User.username == username)
    user = db.scalar(statement)
    if user is None:
        raise AuthError("用户不存在")

    user.display_name = display_name
    db.commit()
    db.refresh(user)

    return UserProfile(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
    )
