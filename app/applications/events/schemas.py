from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.applications.interactions.models import Tag
from app.core.base.schemas import BaseOutSchema
from .models import Event


class EventOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Event)

    @staticmethod
    async def add_tags(item: Event):
        return await Tag.filter(item_type=Tag.ModelType.event, item_id=item.id).values_list("name", flat=True)

    @classmethod
    async def add_fields(cls, item: Event, user):
        is_host = bool(user) and await item.is_host(user)
        is_not_attendee = bool(user) and not await item.attendees.filter(id=user.id).exists()
        return {
            "allowed_actions": {
                "edit": is_host,
                "delete": is_host,
                "attend": is_not_attendee
            },
            "tags": await EventOut.add_tags(item)
        }


class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    links: Optional[dict] = None
    form: Optional[dict] = None
    start_date: datetime
    end_date: datetime
    media: Optional[dict] = None
    qr_code: Optional[dict] = None
    verification_link: Optional[str] = None
    latitude: float
    longitude: float
    category: Optional[str] = None
    tags: Optional[list[str]] = []

    def create_update_dict(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class EventUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    links: Optional[dict]
    form: Optional[dict]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    media: Optional[dict]
    qr_code: Optional[dict]
    verification_link: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    category: Optional[str]
    tags: Optional[list[str]]
