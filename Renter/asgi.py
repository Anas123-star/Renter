"""
ASGI config for Renter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from home.consumers import ChatConsumer, NotificationsConsumer, TenantsConsumer
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Renter.settings')

application = get_asgi_application()

# ws_patterns = [
#     path('chat/<room_code>', ChatConsumer.as_asgi()),
#     path('view_message', NotificationsConsumer.as_asgi())
# ]

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(), 
#     'websocket': AuthMiddlewareStack(
#         URLRouter(ws_patterns)
#         )
# })

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("chat/<room_code>", ChatConsumer.as_asgi()),
                    path("view_messages", NotificationsConsumer.as_asgi()),
                    path("dashboard/tenant_details/<tenant_uid>", TenantsConsumer.as_asgi())
                ]
            )
        ),
    }
)
