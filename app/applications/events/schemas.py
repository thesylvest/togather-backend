from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field
from tortoise.functions import Avg
from datetime import datetime
from typing import Optional

from app.applications.interactions.models import Tag, Rate
from app.core.base.schemas import BaseOutSchema
from app.core.base.media_manager import S3
from .models import Event, Attendee


class EventOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(
        Event,
        exclude=["media", "qr_code", "verification_link"]
    )

    @staticmethod
    async def rate(item: Event):
        return (await Rate.filter(
            item_id=item.id, item_type="Event"
        ).annotate(avg=Avg("rate")).group_by().values("avg"))[0]["avg"]

    @staticmethod
    async def media(item: Event):
        return [await S3.get_file_url(media) for media in item.media]

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
            "edit": is_host,
            "delete": is_host,
            "form_view": is_host,
            "attend": is_not_attendee
        }

    @classmethod
    async def add_fields(cls, item: Event, user):
        return {
            "allowed_actions": await EventOut.allowed_actions(item, user),
            "tags": await EventOut.tags(item),
            "media": await EventOut.media(item),
            "rate": await EventOut.rate(item)
        }


class EventCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    links: Optional[dict] = None
    form: Optional[dict] = None
    start_date: datetime
    end_date: datetime
    media: Optional[list[str]] = None
    latitude: float
    longitude: float
    category_id: int
    tags: Optional[list[str]] = []
    host_club: Optional[int] = None


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    links: Optional[dict] = None
    form: Optional[dict] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    media: Optional[dict] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None
    tags: Optional[list[str]] = []


class EventRate(BaseModel):
    rate: int = Field(..., le=5, ge=1)


class AttendeeOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(
        Attendee,
        exclude=["form_data"]
    )

    @classmethod
    async def add_fields(cls, item: Attendee, user):
        return {
            "form_data": item.form_data if (item.user == user) or (item.event.is_host(user)) else None
        }


class AttendeeCreate(BaseModel):
    form_data: Optional[dict] = None
