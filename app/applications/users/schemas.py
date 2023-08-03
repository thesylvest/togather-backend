from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, validator


class BaseProperties(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={"id", "is_superuser", "is_active"},
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class BaseUser(BaseProperties):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime]


class BaseUserCreate(BaseProperties):
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    username: Optional[str]
    password: str


class BaseUserUpdate(BaseProperties):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    social_links: Optional[str] = None
    birth_date: Optional[str] = None


class BaseUserDB(BaseUser):
    id: int
    password_hash: str
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class BaseUserOut(BaseUser):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    social_links: Optional[dict] = None
    birth_date: Optional[datetime] = None

    class Config:
        from_attributes = True

    def allowed_actions(item, user):
        return ["oh yeah", "baby", str(user is None)]
