from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage


def send_push_message(token, message, notification_type, data={}):
    data['type'] = notification_type

    try:
        PushClient().publish(
            PushMessage(
                to=token,
                body=message,
                data=data
            )
        )
    except:
        pass
