from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from jwt import PyJWTError
import jwt

from app.core.auth.schemas import JWTTokenPayload, CredentialsSchema
from app.applications.users.models import User
from app.core.auth.utils import password
from app.settings import config

password_reset_jwt_subject = "passwordreset"
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login/access-token")


def send_email(email_to: str, subject_template="", html_template="", environment={}):
    pass


def send_reset_password_email(email_to: str, email: str, token: str):
    pass


def send_new_account_email(email_to: str, username: str, password: str):
    pass


def generate_password_reset_token(email):
    pass
    # now = datetime.utcnow()
    # expires = now + timedelta(hours=config.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    # exp = expires.timestamp()
    # encoded_jwt = jwt.encode(
    #   {"exp": exp, "nbf": now, "sub": password_reset_jwt_subject, "email": email},
    #   config.SECRET_KEY,
    #   algorithm=config.JWT_ALGORITHM,
    # )
    # return encoded_jwt


def verify_password_reset_token(token) -> Optional[str]:
    pass
    # try:
    #   decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    #   assert decoded_token["sub"] == password_reset_jwt_subject
    #   return decoded_token["email"]
    # except InvalidTokenError:
    #   return None


async def get_current_user(token: str = Security(reusable_oauth2)) -> Optional[User]:
    pass
    # try:
    #   payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    #   token_data = JWTTokenPayload(**payload)
    # except PyJWTError:
    #   raise HTTPException(
    #       status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    #   )
    # user = await User.get(id=token_data.user_id)
    # if not user:
    #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # return user


async def get_current_active_user(current_user: User = Security(get_current_user)):
    pass
    # if not current_user.is_active:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    # return current_user


async def get_current_active_superuser(current_user: User = Security(get_current_user)):
    pass
    # if not current_user.is_superuser:
    #   raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The user doesn't have enough privileges")
    # return current_user


async def authenticate(credentials: CredentialsSchema) -> Optional[User]:
    pass
    # if credentials.email:
    #   user = await User.get_by_email(credentials.email)
    # elif credentials.username:
    #   user = await User.get_by_username(credentials.username)
    # else:
    #   return None

    # if user is None:
    #   return None

    # verified, updated_password_hash = password.verify_and_update_password(
    #   credentials.password, user.password_hash
    # )

    # if not verified:
    #   return None
    # if updated_password_hash is not None:
    #   user.password_hash = updated_password_hash
    #   await user.save()
    # return user
