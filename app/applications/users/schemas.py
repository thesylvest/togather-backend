from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.core.base.schemas import BaseOutModel


class BaseProperties(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={"is_superuser", "is_active"},
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class UserCreate(BaseProperties):
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    username: Optional[str]
    password: str


class UserUpdate(BaseProperties):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    social_links: Optional[str] = None
    birth_date: Optional[str] = None


class UserOut(BaseOutModel):
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

    @classmethod
    def add_fields(cls, item, user):  # TODO: modify actions related to connections
        if item == user:
            allowed_actions = ["edit"]
        else:
            allowed_actions = ["connect", "block", "hide"]

        return {"allowed_actions": allowed_actions}
