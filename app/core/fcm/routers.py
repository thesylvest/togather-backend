from pyfcm import FCMNotification
from typing import List, Optional


def send_notification(registration_ids: List[str], title: str, body: str, image: Optional[str] = None):
    push_service = FCMNotification(api_key="<Your Firebase Cloud Messaging API Key>")

    result = push_service.notify_multiple_devices(
        registration_ids=registration_ids,
        message_title=title,
        message_body=body,
        message_icon=image
    )

    return result
