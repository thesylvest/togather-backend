from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field

from .models import Notification, Hide, Report, Category
from app.core.base.schemas import BaseOutSchema


class NotificationOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Notification)

    @classmethod
    async def add_fields(cls, item: Notification, user):
        return {
            "notification_data": await item.notification_data()
        }


class HideOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Hide)


class ReportOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Report)


CategoryOut = pydantic_model_creator(Category)


class HideCreate(BaseModel):
    item_id: int
    item_type: Hide.ModelType


class ReportCreate(BaseModel):
    item_id: int
    item_type: Report.ModelType
    reason: str = Field(..., max_length=512)


class RateItem(BaseModel):
    rate: int = Field(..., le=5, ge=1)
