from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr
from tortoise.functions import Count
from tortoise.expressions import Q
from datetime import datetime
from typing import Optional

from app.core.base.schemas import BaseOutSchema
from .models import User, Connection


class UserPydantic(pydantic_model_creator(User, exclude=["university", "categories"])):
    rate: float | None = None


class UserOut(BaseOutSchema):
    pydantic_model = UserPydantic

    @staticmethod
    async def connection(item, user):
        if item == user:
            return Connection.Status.me
        connection = await Connection.get_or_none(
            Q(from_user=user, to_user=item) | Q(from_user=item, to_user=user)
        )
        if connection:
            if connection.is_accepted:
                return Connection.Status.connected
            return Connection.Status.request_sent if connection.from_user == user else Connection.Status.request_received
        return Connection.Status.not_connected

    @staticmethod
    async def allowed_actions(item: User, user: User):
        return {
            "canBlock": user is not None and (item != user) and not await item.blocked_users.filter(id=user.id).exists(),
            "canHide": user is not None and item != user,
            "canUpdate": user is not None and item == user,
            "canDelete": user is not None and item == user,
            "canReport": user is not None and item != user,
        }

    @classmethod
    async def add_fields(cls, item: User, user):
        user = await User.annotate(
            post_count=Count('posts'),
            hosted_event_count=Count('hosted_events'),
            attended_event_count=Count('attended_events')
        ).prefetch_related("categories", "university").get(id=item.id)
        return {
            "requets_data": {
                "allowed_actions": await UserOut.allowed_actions(item, user),
                "connection_status": await UserOut.connection(item, user),
            },
            "post_count": user.post_count,
            "hosted_event_count": user.hosted_event_count,
            "attended_event_count": user.attended_event_count,
            "university": user.university,
            "categories": list(user.categories)
        }


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    social_links: Optional[dict] = None
    birth_date: Optional[datetime] = None
    private_profile: Optional[bool] = None
    university: Optional[int] = None
    media: Optional[list[dict]] = None
    categories: Optional[list[int]] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
