# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
# todo: doc
class ClientStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Добавляем текущее соединение к группе "client_status_group"
        await self.channel_layer.group_add(
            "client_status_group",
            self.channel_name
        )
        # Принимаем соединение WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Удаляем текущее соединение из группы "client_status_group"
        await self.channel_layer.group_discard(
            "client_status_group",
            self.channel_name
        )

    # Этот метод соответствует "type": "send.client.status" в group_send
    async def send_client_status(self, event):
        # Получаем данные из события
        data = event["data"]
        # Отправляем данные через WebSocket-соединение
        await self.send(text_data=json.dumps(data))
