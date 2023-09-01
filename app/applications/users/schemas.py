from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.expressions import Q, Subquery
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.core.base.schemas import BaseOutSchema
from .models import User, Connection


class UserOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(User)

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
        counts = await User.get(id=item.id).annotate(
            post_count=Subquery(item.posts.all().count()),
            hosted_event_count=Subquery(item.hosted_events.all().count()),
            attended_event_count=Subquery(item.attendance.all().count()),
        )
        return {
            "requets_data": {
                "allowed_actions": await UserOut.allowed_actions(item, user),
                "connection_status": await UserOut.connection(item, user),
            },
            "post_count": counts.post_count,
            "hosted_event_count": counts.hosted_event_count,
            "attended_event_count": counts.attended_event_count,
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
    media: list[dict] = None
    categories: list[int] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
