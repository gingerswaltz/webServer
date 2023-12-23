# iot/routing.py
from django.urls import re_path
from .consumers import ClientStatusConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
# todo: doc
websocket_urlpatterns = [
    re_path(r'ws/client-status/$', ClientStatusConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})