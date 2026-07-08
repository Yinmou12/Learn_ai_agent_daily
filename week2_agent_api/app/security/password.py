import hashlib
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    """生成密码哈希。

    返回格式：salt$hash
    salt 用来防止相同密码得到相同哈希。
    """

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    验证用户输入密码是否匹配已保存哈希
    """

    try:
        salt, expected_hash = stored_hash.split("$", maxsplit=1)
    except ValueError:
        return False

    actual_hash = hash_password(password, salt).split("$", maxsplit=1)[1]

    return secrets.compare_digest(actual_hash, expected_hash)
