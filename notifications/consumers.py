import asyncio
import json
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from notifications.models import Notification
from friends.models import FriendList, FriedRequest
from chat.models import UnreadMessages
from chat.exceptions import ClientError
from .utils import LazyNotificationEncoder

User = get_user_model()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = await get_user(self.scope['user'])

    async def disconnect(self, code):
        pass

    async def receive_json(self, content, **kwargs):
        try:
            if content['command'] == 'send':
                if not self.user.is_authenticated:
                    raise ClientError('AUTH ERROR', 'you must be authenticated')
                if not len(content['message'].strip()):
                    raise ClientError(422, "you can't send empty message")

            elif content['command'] == 'old_notification':
                await self.get_old_notification(content['page'])
            elif content['command'] == 'old_chat_notification':
                await self.old_chat_notification(content['page'])
            elif content['command'] == 'accept_request':
                await self.accept_friend(content['notification_id'])
            elif content['command'] == 'decline_request':
                await self.decline_friend(content['notification_id'])
            elif content['command'] == 'refresh_notification':
                await self.refresh_notifcation(content.get('last_timestamp'))
            elif content['command'] == 'refresh_chat_notification':
                await self.refresh_chat_notifcation(content.get('last_timestamp'))
            elif content['command'] == 'mark_as_read':
                await mark_notification_as_read(self.user)


        except ClientError as e:
            await self.send_error_message(e)

    async def chat_message(self, content):
        await self.send_json(content)

    async def send_error_message(self, e):
        error_data = {}
        error_data['type'] = 'error'
        error_data['error'] = e.code
        error_data['message'] = e.message
        await self.send_json(error_data)

    async def get_old_notification(self, page):
        if not self.user.is_authenticated:
            raise ClientError('AUTH ERROR', 'you must be authenticated')
        data = await get_old_notification(self.user, page)
        unread_count = await unread_notification_count(self.user)
        data['unread_count'] = unread_count
        await self.send_json(data)

    async def old_chat_notification(self, page):
        if not self.user.is_authenticated:
            raise ClientError('AUTH ERROR', 'you must be authenticated')
        data = await get_old_chat_notification(self.user, page)
        unread_count = await unread_chat_notification_count(self.user)
        data['unread_count'] = unread_count
        await self.send_json(data)

    async def accept_friend(self, notification_id):
        new_notification = await accept_friend_request(self.user, notification_id)
        await self.send_json({
            'type': 'notification_update',
            'notification': new_notification,
        })

    async def decline_friend(self, notification_id):
        new_notification = await decline_friend_request(self.user, notification_id)
        await self.send_json({
            'type': 'notification_update',
            'notification': new_notification,
        })

    async def refresh_notifcation(self, timestamp):
        if not timestamp:
            timestamp = str(datetime.now() - timedelta(hours=24))
        data = await notification_after_timestamp(self.user, timestamp)
        unread_count = await unread_notification_count(self.user)
        data['unread_count'] = unread_count
        await self.send_json(data)

    async def refresh_chat_notifcation(self, timestamp):
        if not timestamp:
            timestamp = str(datetime.now() - timedelta(hours=24))
        data = await chat_notification_after_timestamp(self.user, timestamp)
        unread_count = await unread_chat_notification_count(self.user)
        data['unread_count'] = unread_count
        await self.send_json(data)


@database_sync_to_async
def get_user(user):
    if user.is_authenticated:
        user = User.objects.get(id=user.id)
    return user


@database_sync_to_async
def accept_friend_request(user, notification_id):
    if not user.is_authenticated:
        raise ClientError('AUTH ERROR', 'you must be authenticated')
    notification = Notification.objects.get(id=notification_id)
    friend_request = notification.content_object
    if friend_request.receiver != user:
        raise ClientError('', "unexpected error")
    new_notification = friend_request.accept()
    response = json.dumps(new_notification, cls=LazyNotificationEncoder)
    return response


@database_sync_to_async
def decline_friend_request(user, notification_id):
    if not user.is_authenticated:
        raise ClientError('AUTH ERROR', 'you must be authenticated')
    notification = Notification.objects.get(id=notification_id)
    friend_request = notification.content_object
    if friend_request.receiver != user:
        raise ClientError('', "unexpected error")
    new_notification = friend_request.decline()
    response = json.dumps(new_notification, cls=LazyNotificationEncoder)
    return response

@database_sync_to_async
def get_old_notification(user, page):
    friend_request_ct = ContentType.objects.get_for_model(FriedRequest)
    friend_list_ct = ContentType.objects.get_for_model(FriendList)
    notification = Notification.objects.filter(target=user,
                                               content_type__in=[friend_list_ct, friend_request_ct],
                                               ).order_by('-timestamp')
    paginator = Paginator(notification, 10)
    current_page = paginator.get_page(page)
    old_messages = json.dumps(list(current_page.object_list), cls=LazyNotificationEncoder)
    data = {
        'type': 'old_notification',
        'notifications': json.loads(old_messages),
        'next_page': current_page.next_page_number() if current_page.has_next() else None
    }
    if data['notifications']:
        data['last_timestamp'] = data['notifications'][-1]['timestamp']
    return data


@database_sync_to_async
def get_old_chat_notification(user, page):
    ct = ContentType.objects.get_for_model(UnreadMessages)
    notification = Notification.objects.filter(target=user,
                                               content_type=ct,
                                               ).order_by('-timestamp')
    paginator = Paginator(notification, 10)
    current_page = paginator.get_page(page)
    old_messages = json.dumps(list(current_page.object_list), cls=LazyNotificationEncoder)
    data = {
        'type': 'old_chat_notification',
        'notifications': json.loads(old_messages),
        'next_page': current_page.next_page_number() if current_page.has_next() else None
    }
    if data['notifications']:
        data['last_timestamp'] = data['notifications'][-1]['timestamp']
    return data


@database_sync_to_async
def notification_after_timestamp(user, timestamp):
    friend_request_ct = ContentType.objects.get_for_model(FriedRequest)
    friend_list_ct = ContentType.objects.get_for_model(FriendList)
    last_timestamp = datetime.fromisoformat(timestamp)
    all_notification = Notification.objects.filter(target=user,
                                               content_type__in=[friend_list_ct, friend_request_ct],
                                               timestamp__gte=last_timestamp
                                               ).order_by('-timestamp')
    notifications = json.dumps(list(all_notification), cls=LazyNotificationEncoder)
    data = {
        'type': 'refresh_notification',
        'notifications': json.loads(notifications),
    }
    if data['notifications']:
        data['last_timestamp'] = data['notifications'][-1]['timestamp']
    return data


@database_sync_to_async
def chat_notification_after_timestamp(user, timestamp):
    ct = ContentType.objects.get_for_model(UnreadMessages)
    last_timestamp = datetime.fromisoformat(timestamp)
    all_notification = Notification.objects.filter(target=user,
                                                   content_type=ct,
                                                   timestamp__gte=last_timestamp
                                                   ).order_by('-timestamp')
    notifications = json.dumps(list(all_notification), cls=LazyNotificationEncoder)
    data = {
        'type': 'refresh_chat_notification',
        'notifications': json.loads(notifications),
    }
    if data['notifications']:
        data['last_timestamp'] = data['notifications'][-1]['timestamp']
    return data


@database_sync_to_async
def unread_notification_count(user):
    friend_request_ct = ContentType.objects.get_for_model(FriedRequest)
    friend_list_ct = ContentType.objects.get_for_model(FriendList)
    all_notification = Notification.objects.filter(target=user,
                                                   content_type__in=[friend_list_ct, friend_request_ct],
                                                   read=False
                                                   )
    return all_notification.count()


@database_sync_to_async
def unread_chat_notification_count(user):
    ct = ContentType.objects.get_for_model(UnreadMessages)
    all_notification = Notification.objects.filter(target=user,
                                                   content_type=ct,
                                                   read=False
                                                   )
    return all_notification.count()


@database_sync_to_async
def mark_notification_as_read(user):
    friend_request_ct = ContentType.objects.get_for_model(FriedRequest)
    friend_list_ct = ContentType.objects.get_for_model(FriendList)
    unread_notification = Notification.objects.filter(target=user,
                                                   content_type__in=[friend_list_ct, friend_request_ct],
                                                   read=False
                                                   )
    for notification in unread_notification:
        notification.read = True
        notification.save()