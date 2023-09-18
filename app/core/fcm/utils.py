from tortoise.queryset import QuerySet
from firebase_admin import messaging
from tortoise.expressions import F
from copy import copy

from app.applications.users.models import User
from app.main import firebase_app
from .models import FCMDevice

MAX_BATCH_SIZE = 500  # This is firebase cloud messaging limit


async def send_notification(users: QuerySet, title, body, image):
    def prepare_message(message: messaging.Message, token):
        message.token = token
        return copy(message)
    user_ids = await users.values_list("id", flat=True)
    await User.filter(id__in=user_ids).update(unread_notifications=F('unread_notifications') + 1)
    registration_ids = await FCMDevice.filter(user_id__in=user_ids).values_list("registration_id", flat=True)
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        )
    )
    responses: list[messaging.SendResponse] = []
    for i in range(0, len(registration_ids), MAX_BATCH_SIZE):
        messages = [
            prepare_message(message, token)
            for token in registration_ids[i:i + MAX_BATCH_SIZE]
        ]
        responses.extend(
            messaging.send_all(
                messages, app=firebase_app
            ).responses
        )
    return messaging.BatchResponse(responses)
