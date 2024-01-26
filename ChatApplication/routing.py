from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, include
from django.core.asgi import get_asgi_application
from public_chat.consumers import PublicChatConsumer
from chat.consumer import ChatConsumer
from notifications.consumers import NotificationConsumer


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('notification/', NotificationConsumer().as_asgi()),
                path('public_chat/<int:room_id>/', PublicChatConsumer().as_asgi()),
                path('chat/<int:room_id>/', ChatConsumer().as_asgi()),
            ])
        )
    )
})
