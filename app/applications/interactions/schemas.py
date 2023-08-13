from tortoise.contrib.pydantic import pydantic_model_creator

from app.core.base.schemas import BaseOutSchema
from .models import Notification


class NotificationOut(BaseOutSchema):
    pydantic_model = pydantic_model_creator(Notification, exclude=("sent_to", ))
