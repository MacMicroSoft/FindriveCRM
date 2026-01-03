import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . services import create_message, creat_chat, get_chat
from .models import SenderChoice
from .tasks import handle_ws_message, test_task
import uuid


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content):
        print(content)
        payload = {
            "message_uuid": str(uuid.uuid4()),
            "chat_id": content["chat_id"],
            "text": content["text"],
            "sender": content["sender"]
        }

        print(f'[CONSUMER] -> {payload}')

        test_task.delay()
        handle_ws_message.delay(payload)

        await self.send_json({
            "status": "queued",
            "message_uuid": payload["message_uuid"]
        })