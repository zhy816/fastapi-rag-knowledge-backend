from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """
    把用户输入的明文密码转换成密码哈希。

    例如：
    123456 -> $argon2id$v=19$...
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码和数据库里保存的哈希是否匹配。

    plain_password：用户登录时输入的密码
    hashed_password：数据库 users.password_hash 字段里保存的值
    """
    return password_hash.verify(plain_password, hashed_password)