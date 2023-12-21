from .models import FriedRequest
from enum import Enum


def is_request_send(sender, receiver):
    try:
        return FriedRequest.objects.get(sender=sender, receiver=receiver, is_active=True)
    except FriedRequest.DoesNotExist:
        return False


class FriendRequestStatus(Enum):
    NO_REQUEST_SENT = -1
    THEM_SENT_TO_YOU = 0
    YOU_SENT_TO_THEM = 1
