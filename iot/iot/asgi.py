# iot/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
# todo: doc

from main.routing import websocket_urlpatterns


from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Для обработки HTTP запросов
    "websocket": URLRouter(websocket_urlpatterns),  # Для обработки WebSocket запросов
})
