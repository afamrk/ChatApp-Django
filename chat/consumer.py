import json
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import PrivateChatRoom, PrivateChatMessage, UnreadMessages
from django.utils.html import escape
from datetime import datetime

from chat.utils import calculate_timestamp
from chat.exceptions import ClientError

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.room = None
        self.user = await get_user(self.scope['user'])

    async def disconnect(self, code):
        await self.leave_room(self.user, self.room)

    async def receive_json(self, content, **kwargs):
        try:
            if content['command'] == 'send':
                if not self.user.is_authenticated:
                    raise ClientError('AUTH ERROR', 'you must be authenticated')
                if not len(content['message'].strip()):
                    raise ClientError(422, "you can't send empty message")
                await self.send_to_group(content['message'])

            elif content['command'] == 'old_messages':
                await self.get_old_messages(content['page'], self.room)

            elif content['command'] == 'join':
                self.room = await get_chat_room_or_error(content['room_id'])
                await self.join_room(self.room)

            elif content['command'] == 'remove':
                await self.leave_room(self.user, self.room)

        except ClientError as e:
            await self.send_error_message(e)

    async def send_to_group(self, content):
        content = escape(content)
        user = self.user
        if not self.room:
            raise ClientError('ERROR', 'Unexpected error')
        await save_message_to_db(self.room, self.user, content)
        await append_unread_messages(self.room, self.user, content)
        await self.channel_layer.group_send(
            self.room.group_name,
            {
                'type': 'chat.message',
                'username': user.username,
                'user_id': user.id,
                'profile_image': user.profile_image.url,
                'message': content,
                'natural_timestamp': calculate_timestamp(datetime.now())
            }
        )

    async def chat_message(self, content):
        await self.send_json(content)

    async def join_room(self, room):

        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name
        )

        await connect_user(self.room, self.user)
        await on_user_connect(self.room, self.user)

        await self.send_json({
            'type': 'join',
            'success': True
        })

        print(f'{self.user} is connected to {room.id}')

    async def leave_room(self, user, room):
        if not room:
            raise ClientError('ERROR', 'Unexpected Error')

        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name
        )
        await disconnect_user(self.room, self.user)
        print(f'{self.user} is disconnected from {room.id}')
        self.room = None

    async def send_error_message(self, e):
        error_data = {}
        error_data['type'] = 'error'
        error_data['error'] = e.code
        error_data['message'] = e.message
        await self.send_json(error_data)

    async def get_old_messages(self, page, room):
        if not room:
            raise ClientError('Unexpected', 'Unexpected error')
        data = await get_old_messages(room, page)
        await self.send_json(data)


@database_sync_to_async
def get_user(user):
    if user.is_authenticated:
        user = User.objects.get(id=user.id)
    return user


@database_sync_to_async
def get_old_messages(room, page):
    paginator = Paginator(PrivateChatMessage.objects.by_room(room), 10)
    current_page = paginator.get_page(page)
    old_messages = json.dumps(list(current_page.object_list), cls=LazyEncoder)
    data = {
        'type': 'old_message',
        'messages': json.loads(old_messages),
        'next_page': current_page.next_page_number() if current_page.has_next() else None
    }
    return data


@database_sync_to_async
def get_chat_room_or_error(room_id) -> PrivateChatRoom:
    try:
        room = PrivateChatRoom.objects.get(id=room_id)
    except PrivateChatRoom.DoesNotExist:
        raise ClientError('INVALID CHAT ROOM', 'invalid chat room')
    return room


@database_sync_to_async
def save_message_to_db(room, user, message):
    return PrivateChatMessage.objects.create(chat_room=room, user=user, content=message)


@database_sync_to_async
def connect_user(room: PrivateChatRoom, user):
    room.connect_user(user)


@database_sync_to_async
def disconnect_user(room: PrivateChatRoom, user):
    room.disconnect_user(user)


@database_sync_to_async
def append_unread_messages(room, user, message):
    other_user = room.user2 if room.user1 == user else room.user1
    if other_user not in room.connected_users.all():
        try:
            unread_message = UnreadMessages.objects.get(user=other_user, room=room)
            unread_message.recent_message = message
            unread_message.count += 1
            unread_message.save()
        except UnreadMessages.DoesNotExist:
            UnreadMessages(user=other_user, room=room, recent_message=message, count=1).save()


@database_sync_to_async
def on_user_connect(room, user):
    try:
        unread_message = UnreadMessages.objects.get(user=user, room=room)
        unread_message.count = 0
        unread_message.save()
    except UnreadMessages.DoesNotExist:
        UnreadMessages(user=user, room=room).save()


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PrivateChatMessage):
            return {
                'message_id': obj.id,
                'message': obj.content,
                'username': obj.user.username,
                'user_id': obj.user.id,
                'profile_image': obj.user.profile_image.url,
                'natural_timestamp': calculate_timestamp(obj.timestamp)
            }
        else:
            return super().default(obj)



