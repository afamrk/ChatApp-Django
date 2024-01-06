from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from .models import PrivateChatRoom


def get_or_create_private_chat(user1, user2):
    try:
        chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
    except PrivateChatRoom.DoesNotExist:
        chat, _ = PrivateChatRoom.objects.get_or_create(user1=user2, user2=user1)
    return chat


def calculate_timestamp(timestamp):
    day = naturalday(timestamp)
    if day in {'today', 'yesterday'}:
        str_time = datetime.strftime(timestamp, "%I:%M %p")
        str_time = str_time.strip("0")
        ts = f"{naturalday(timestamp)} at {str_time}"
        # other days
    else:
        str_time = datetime.strftime(timestamp, "%m/%d/%Y")
        ts = f"{str_time}"
    return str(ts)
