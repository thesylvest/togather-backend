from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi import status

from app.settings import config
from app.core.base.exceptions import APIException


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


def create_access_token_from_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        if username is None or email is None or user_id is None:
            raise APIException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except ExpiredSignatureError:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            message="Login required",
        )
    except JWTError:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            message="Login required",
        )

    return create_access_token(
        data={"username": username, "email": email, "user_id": user_id},
        expires_delta=timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
