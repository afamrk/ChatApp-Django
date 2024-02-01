import json
from .models import Notification
from django.contrib.humanize.templatetags.humanize import naturaltime


class LazyNotificationEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Notification):
            data = {
                'notification_type': obj.content_type.model,
                'notification_id': str(obj.pk),
                'verb': obj.verb,
                'is_read': str(obj.read),
                'natural_timestamp': str(naturaltime(obj.timestamp)),
                'timestamp': str(obj.timestamp),
                'from': {
                    'image_url': obj.from_user.profile_image.url
                },
                'actions': {
                    'redirect_url': obj.redirect_url
                }
            }
            if data['notification_type'] == "friedrequest":
                data['is_active'] = obj.content_object.is_active
            if data['notification_type'] == "unreadmessages":
                data['from']['name'] = obj.content_object.other_user().username
            return data
        else:
            return super().default(obj)
