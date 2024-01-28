from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import PrivateChatRoom, PrivateChatMessage

User = get_user_model()

# Create your views here.
@login_required
def private_chat_room(request):
    context = {}

    friend_id = request.GET.get('friend_id')
    if friend_id:
        try:
            friend = User.objects.get(id=friend_id)
            query = Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user)
            PrivateChatRoom.objects.get(query)
            context['friend_id'] = friend.id
        except Exception:
            return HttpResponseForbidden()
    query = Q(user1=request.user) | Q(user2=request.user)
    user_chats = PrivateChatRoom.objects.filter(query)
    m_and_f = []
    for chat in user_chats:
        last_message = PrivateChatMessage.objects.filter(chat_room=chat).last()
        if last_message:
            message = last_message.content
        else:
            message = ''
        m_and_f.append({
            'message': message,
            'room_id': chat.id,
            'friend': chat.user2 if chat.user1 == request.user else chat.user1
        })
    context['is_debug'] = settings.DEBUG
    context['m_and_f'] = m_and_f
    return render(request, 'chat/room.html', context)