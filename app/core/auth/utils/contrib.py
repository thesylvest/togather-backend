from datetime import datetime, timedelta
from typing import Optional, Annotated

from fastapi import HTTPException, Security, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.auth.schemas import JWTTokenPayload, CredentialsSchema, JWTTokenData, JWTToken
from app.applications.users.models import User
from app.core.auth.utils import password
from app.settings import config

from google.oauth2 import id_token
from google.auth.transport import requests

password_reset_jwt_subject = "passwordreset"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/access-token")


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


async def get_current_user(token: str = Security(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = JWTTokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await User.get_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None
    
    return await get_current_user(token)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
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
    if credentials.email:
        user = await User.get_by_email(credentials.email)
    elif credentials.username:
        user = await User.get_by_username(credentials.username)
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
        # Verify and decode the Google ID token
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        return id_info
    except ValueError as e:
        print("Error decoding Google token:", e)
        return None