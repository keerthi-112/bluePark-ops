"""
ASGI config for bluepark project.

Routes HTTP through Django as usual and WebSocket connections through
Channels. get_asgi_application() must run before anything below imports
app code that touches models (kitchen.routing -> kitchen.consumers),
so the Django app registry is populated first.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluepark.settings.dev')

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

from kitchen.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
