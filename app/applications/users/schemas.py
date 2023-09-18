from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr, Field
from tortoise.expressions import Q, Subquery
from typing import Optional
from datetime import date

from app.core.base.schemas import BaseOutSchema
from .models import User, Connection, Blocked


class UserOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(User)

    @staticmethod
    async def location(item: User):
        if not item.private_profile:
            return {
                "latitude": item.latitude,
                "longitude": item.longitude
            }

    @staticmethod
    async def allowed_actions(item: User, user: User, can_connect):
        return {
            "can_block": user is not None and (item != user),
            "can_connect": user is not None and (item != user) and can_connect,
            "can_hide": user is not None and item != user,
            "can_update": user is not None and item == user,
            "can_delete": user is not None and item == user,
            "can_report": user is not None and item != user,
        }

    @classmethod
    async def add_fields(cls, item: User, user):
        counts = await User.get(id=item.id).annotate(
            post_count=Subquery(item.posts.all().count()),
            hosted_event_count=Subquery(item.hosted_events.all().count()),
            attended_event_count=Subquery(item.attendance.all().count()),
        )
        connection_count = await Connection.filter(is_accepted=True).filter(Q(from_user=item) | Q(to_user=item)).count()
        is_blocked_by = await Blocked.filter(blocking_user=item, blocked_user=user).exists()
        is_blocked = await Blocked.filter(blocked_user=item, blocking_user=user).exists()
        return {
            "request_data": {
                "allowed_actions": await UserOut.allowed_actions(item, user, not (is_blocked_by or is_blocked)),
                "connection_status": Connection.Status.not_connected if user is None else await user.connection_status(item),
                "is_blocked_by": is_blocked_by,
                "is_blocked": is_blocked
            },
            "latitude": item.latitude if (not item.private_profile) or (item == user) else None,
            "longitude": item.longitude if (not item.private_profile) or (item == user) else None,
            "post_count": counts.post_count,
            "connection_count": connection_count,
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
    birth_date: Optional[date] = None
    private_profile: Optional[bool] = None
    university_id: Optional[int] = None
    media: list[dict] = Field(None, max_length=5)
    interests: list[int] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
