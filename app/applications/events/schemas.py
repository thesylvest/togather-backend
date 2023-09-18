from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.expressions import Subquery
from pydantic import BaseModel, Field
from tortoise.functions import Avg
from datetime import datetime
from typing import Optional
import pytz

from app.applications.interactions.models import Tag, Rate
from app.core.base.schemas import BaseOutSchema
from .models import Event, Attendee


class EventOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Event)

    @staticmethod
    async def rate(item: Event):
        return (await Rate.filter(
            item_id=item.id, item_type="Event"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @staticmethod
    async def tags(item: Event):
        return await Tag.filter(
            item_type="Event",
            item_id=item.id
        ).values_list("name", flat=True)

    @staticmethod
    async def allowed_actions(item: Event, user, is_host):
        is_verified_attendee = bool(user) and await item.can_post(user)
        can_attend = bool(user) and item.end_date > datetime.now(pytz.utc)
        return {
            "can_edit": is_host,
            "can_delete": is_host,
            "view_form": is_host,
            "can_attend": can_attend,
            "can_post": is_verified_attendee,
            "can_rate": is_verified_attendee,
        }

    @classmethod
    async def add_fields(cls, item: Event, user):
        item = await Event.annotate(
            attendee_count=Subquery(item.attendees.all().count()),
            rate_count=Subquery(Rate.filter(item_id=item.id, item_type="Event").count())
        ).prefetch_related("host_club").get(id=item.id)
        user_rate = await Rate.get_or_none(item_id=item.id, item_type="Event")
        is_attending = bool(user) and await item.attendees.filter(id=user.id).exists()
        is_host = bool(user) and await item.is_host(user)
        return {
            "request_data": {
                "allowed_actions": await EventOut.allowed_actions(item, user, is_host),
                "user_rate": user_rate.rate if user_rate else None,
                "is_attending": is_attending,
                "is_hosting": is_host
            },
            "tags": await EventOut.tags(item),
            "rate": await EventOut.rate(item),
            "rate_count": item.rate_count,
            "attendee_count": item.attendee_count,
        }


class AttendeeOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Attendee)

    @classmethod
    async def add_fields(cls, item: Attendee, user):
        if (item.user == user) or (await item.event.is_host(user)):
            return {"form_data": item.form_data}
        return {}


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    links: Optional[dict] = None
    form: Optional[dict] = None
    media: list[dict] = Field(None, max_length=5)
    tags: Optional[list[str]] = []


class EventCreate(EventUpdate):
    name: str = Field(..., max_length=255)
    category_id: int
    start_date: datetime
    end_date: datetime
    host_club_id: Optional[int] = None


class AttendeeCreate(BaseModel):
    form_data: Optional[dict] = None
