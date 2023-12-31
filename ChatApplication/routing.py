from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django.core.asgi import get_asgi_application
from public_chat.consumers import PublicChatConsumer


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('public_chat/<int:room_id>/', PublicChatConsumer().as_asgi())
            ])
        )
    )
})
