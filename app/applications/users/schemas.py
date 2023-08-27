from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.base.schemas import BaseOutSchema
from .models import User, Connection


class UserOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(User)

    @staticmethod
    async def connection(item, user):
        if item == user:
            return Connection.Status.me
        sent: Connection = await Connection.get_or_none(from_user=user, to_user=item)
        if sent:
            if sent.is_accepted:
                return Connection.Status.connected
            return Connection.Status.request_sent
        recv: Connection = await Connection.get_or_none(from_user=item, to_user=user)
        if recv:
            if recv.is_accepted:
                return Connection.Status.connected
            return Connection.Status.request_received
        return Connection.Status.not_connected

    @staticmethod
    async def allowed_actions(item, user):
        allowed_actions = {"block": True, "hide": True}
        return allowed_actions

    @classmethod
    async def add_fields(cls, item, user):
        return {
            "requets_data": {
                "allowed_actions": await UserOut.allowed_actions(item, user),
                "connection_status": await UserOut.connection(item, user),
            }
        }


class UserCreate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: EmailStr
    username: Optional[str]
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    social_links: Optional[str] = None
    birth_date: Optional[str] = None
