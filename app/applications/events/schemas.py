from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.functions import Avg, Count
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.applications.interactions.models import Tag, Rate
from app.core.base.schemas import BaseOutSchema
from app.core.base.media_manager import S3
from .models import Event, Attendee


class EventOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Event)

    @staticmethod
    async def rate(item: Event):
        return (await Rate.filter(
            item_id=item.id, item_type="Event"
        ).annotate(avg=Avg("rate")).values("avg"))[0]["avg"]

    @staticmethod
    async def media(item: Event):
        return [S3.get_file_url(media) for media in item.media]

    @staticmethod
    async def tags(item: Event):
        return await Tag.filter(
            item_type=Tag.ModelType.event,
            item_id=item.id
        ).values_list("name", flat=True)

    @staticmethod
    async def allowed_actions(item: Event, user):
        is_host = bool(user) and await item.is_host(user)
        is_not_attendee = bool(user) and not await item.attendees.filter(id=user.id).exists()
        return {
            "canEdit": is_host,
            "canDelete": is_host,
            "viewForm": is_host,
            "canAttend": is_not_attendee,
        }

    @classmethod
    async def add_fields(cls, item: Event, user):
        item = await Event.annotate(
            attendee_count=Count('attendees'),
        ).get(id=item.id)
        return {
            "request_data": {
                "allowed_actions": await EventOut.allowed_actions(item, user),
            },
            "tags": await EventOut.tags(item),
            "media": await EventOut.media(item),
            "rate": await EventOut.rate(item),
            "attendee_count": item.attendee_count,
        }


class AttendeeOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Attendee)

    @classmethod
    async def add_fields(cls, item: Attendee, user):
        if (item.user == user) or (item.event.is_host(user)):
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
    media: Optional[list[dict]] = None
    tags: Optional[list[str]] = []


class EventCreate(EventUpdate):
    name: str = Field(..., max_length=255)
    latitude: float
    longitude: float
    category_id: int
    start_date: datetime
    end_date: datetime
    host_club_id: Optional[int] = None


class AttendeeCreate(BaseModel):
    form_data: Optional[dict] = None
