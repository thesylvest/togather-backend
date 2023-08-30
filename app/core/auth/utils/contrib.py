from datetime import datetime, timedelta
from typing import Optional, Annotated

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import JWTError
from jose import jwt

from app.core.auth.schemas import CredentialsSchema
from app.applications.users.models import User
from app.core.auth.utils import password
from app.settings import config

from google.oauth2 import id_token
from google.auth.transport import requests

password_reset_jwt_subject = "passwordreset"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/access-token", auto_error=False)


def generate_password_reset_token(email):
    now = datetime.utcnow()
    expires = now + timedelta(hours=config.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": password_reset_jwt_subject, "email": email},
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )

    return encoded_jwt


def verify_password_reset_token(token) -> Optional[str]:
    try:
        decoded_token = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        assert decoded_token["sub"] == password_reset_jwt_subject
        return decoded_token["email"]
    except AssertionError:
        return None


async def get_current_user_optional(token: Optional[str] = Security(oauth2_scheme)):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None
    except JWTError:
        return None
    return await User.get_or_none(id=user_id)


async def get_current_user(user: User = Depends(get_current_user_optional)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_user_optional(
    current_user: User | None = Depends(get_current_user_optional)
):
    if current_user and not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(current_user: User = Security(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )
    return current_user


async def authenticate(credentials: CredentialsSchema) -> Optional[User]:
    if credentials.username:
        user = await User.get_or_none(username=credentials.username)
    else:
        return None

    if user is None:
        return None

    verified, updated_password_hash = password.verify_and_update_password(
        credentials.password, user.password_hash
    )

    if not verified:
        return None

    if updated_password_hash is not None:
        user.password_hash = updated_password_hash
        await user.save()

    return user


def decode_google_token(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        return id_info
    except ValueError as e:
        print("Error decoding Google token:", e)
        return None
