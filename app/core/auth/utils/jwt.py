from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi import status, HTTPException
from datetime import datetime, timedelta
from jose import jwt

from app.settings import config


def encode_jwt(data: dict):
    return jwt.encode(data, config.SECRET_KEY, config.JWT_ALGORITHM)


def decode_jwt(token: str):
    return jwt.decode(token, config.SECRET_KEY, config.JWT_ALGORITHM)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return encode_jwt(to_encode)


def create_refresh_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(minutes=config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return encode_jwt(to_encode)


def create_access_token_from_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        if username is None or email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return create_access_token(
        data={"username": username, "email": email, "user_id": user_id},
    ), payload
