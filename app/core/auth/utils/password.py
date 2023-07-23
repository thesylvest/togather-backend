from passlib.context import CryptContext
from typing import Tuple
from passlib import pwd

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_and_update_password(plain_password: str, hashed_password: str) -> Tuple[bool, str]:
    pass
    # return pwd_context.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    pass
    # return pwd_context.hash(password)


def generate_password() -> str:
    pass
    # return pwd.genword()
