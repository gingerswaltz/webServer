# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ClientStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "client_status_group",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "client_status_group",
            self.channel_name
        )

    # Этот метод соответствует "type": "send.client.status" в group_send
    async def send_client_status(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
