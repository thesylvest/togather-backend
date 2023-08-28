from tortoise.queryset import QuerySet
from firebase_admin import messaging
from copy import copy

from app.main import firebase_app
from .models import FCMDevice


MAX_MESSAGES_PER_BATCH = 500


def prepare_message(message: messaging.Message, token):
    message.token = token
    return copy(message)


async def send_notification(users: QuerySet, title, body, image):
    registration_ids = await FCMDevice.filter(user__in=users).values_list("registration_id", flat=True)
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        )
    )
    responses: list[messaging.SendResponse] = []
    for i in range(0, len(registration_ids), MAX_MESSAGES_PER_BATCH):
        messages = [
            prepare_message(message, token)
            for token in registration_ids[i:i + MAX_MESSAGES_PER_BATCH]
        ]
        responses.extend(
            messaging.send_all(
                messages, app=firebase_app
            ).responses
        )
    return messaging.BatchResponse(responses)
