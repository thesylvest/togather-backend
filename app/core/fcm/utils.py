from firebase_admin import messaging


def send_notification(registration_ids, title, body, image):
    batch_tokens = [registration_ids[i:i + 100] for i in range(0, len(registration_ids), 100)]
    for batch in batch_tokens:
        try:
            send_notification_low(batch, title, body, image)
        except Exception:
            pass  # TODO: logging error


def send_notification_low(registration_ids, title, body, image):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image,
        ),
        tokens=registration_ids,
    )

    response = messaging.send_multicast(message)
    for resp in response.responses:
        if resp.success:
            print('Successfully sent message:', resp.message_id)
        else:
            print('Failed to send message:', resp.exception)
