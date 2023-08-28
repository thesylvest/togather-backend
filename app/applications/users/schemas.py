from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr
from tortoise.expressions import Q
from tortoise import fields
from typing import Optional

from app.core.base.schemas import BaseOutSchema
from .models import User, Connection


class AbstractUser(User):
    class Meta:
        abstract = True
    rate = fields.FloatField(default=0)


class UserOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(
        AbstractUser,
        exclude=User.PydanticMeta.exclude + ("blockeds", "attendance", "rates", "ownerships", "blocked_users", "received_connections", "sent_connections", "posts", "comments", "form_responses", "reports", "reports", "hides", "devices", "memberships", "hosted_events", "attended_events", "places", "notifiactions", "clubs", "unread_notifications", "blocking", "blocked"),
    )

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
        await item.fetch_related("posts", "hosted_events", "attended_events")
        return {
            "requets_data": {
                "allowed_actions": await UserOut.allowed_actions(item, user),
                "connection_status": await UserOut.connection(item, user),
            },
            "post_count": len(item.posts),
            "hosted_event_count": len(item.hosted_events),
            "attended_event_count": len(item.attended_events),
        }


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
    private_profile: Optional[bool] = None
    university: Optional[str] = None
    media: Optional[list[dict]] = None
    categories: Optional[list[str]] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
