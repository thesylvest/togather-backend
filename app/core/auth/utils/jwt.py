from datetime import datetime, timedelta
import jwt

from app.settings import config


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    pass
    # to_encode = data.copy()
    # if expires_delta:
    #   expire = datetime.utcnow() + expires_delta
    # else:
    #   expire = datetime.utcnow() + timedelta(minutes=15)
    # to_encode.update({"exp": expire, "sub": "access"})
    # return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)
