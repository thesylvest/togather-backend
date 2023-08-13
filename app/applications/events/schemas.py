from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.base.schemas import BaseOutSchema
from .models import Event


class EventOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Event)

    @classmethod
    def add_fields(cls, item, user):  # TODO: Implement correct queries
        return {
            "allowed_actions": ["edit and delete if host", "attend if not attendee"]
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

    def create_update_dict(self):
        return self.dict(exclude_unset=True, exclude={"id"})
