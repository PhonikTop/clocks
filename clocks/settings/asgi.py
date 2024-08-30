import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from ws.rounting import ws_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(
        ws_urlpatterns
    ))
})
