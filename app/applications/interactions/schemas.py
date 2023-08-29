from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field

from app.core.base.schemas import BaseOutSchema
from .models import Notification, Hide, Report


class NotificationOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Notification, exclude=("sent_to", ))


class HideOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Hide)

    @classmethod
    async def add_fields(cls, item: Hide, user):
        return {
            "item": (await item.get_item())[1]
        }


class ReportOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Report)

    @classmethod
    async def add_fields(cls, item: Hide, user):
        return {
            "item": (await item.get_item())[1]
        }


class HideCreate(BaseModel):
    item_id: int
    item_type: Hide.ModelType


class ReportCreate(BaseModel):
    item_id: int
    item_type: Report.ModelType
    reason: str = Field(..., max_length=512)
