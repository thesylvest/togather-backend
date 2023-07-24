from datetime import datetime, timedelta
from jose import jwt

from app.settings import config


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire, "sub": "access"})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)
