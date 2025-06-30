"""
ASGI config for authentication project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set the default Django settings module before importing other Django stuff
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication.settings')

# This must come AFTER setting DJANGO_SETTINGS_MODULE
django_asgi_app = get_asgi_application()

# Now it's safe to import other Django-related modules
import django
django.setup()

# Import your routing after Django is setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})