from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.core.base.schemas import BaseOutSchema


class EventOut(BaseOutSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    links: Optional[dict] = None
    form: Optional[dict] = None
    start_date: datetime
    end_date: datetime
    media: Optional[dict] = None
    rate: float
    qr_code: Optional[dict] = None
    verification_link: Optional[str] = None
    host: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None

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
