from .models import Notification, NotificationType
from app.core.base.schemas import BaseOutModel


class NotificationOut(BaseOutModel):
    @classmethod
    def add_fields(cls, item: Notification, user):
        match item.type:
            case NotificationType.user:
                return {"type": "user"}
            case NotificationType.post:
                return {"type": "post"}
            case NotificationType.event:
                return {"type": "event"}
            case NotificationType.like:
                return {"type": "like"}
            case NotificationType.comment:
                return {"type": "comment"}
        return {"type": "invalid"}
