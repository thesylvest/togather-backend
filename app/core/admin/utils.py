from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException
from passlib.context import CryptContext

from .models import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


security = HTTPBasic()


async def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    admin = await Admin.get_or_none(username=credentials.username)
    if not admin or not verify_password(credentials.password, admin.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return admin
