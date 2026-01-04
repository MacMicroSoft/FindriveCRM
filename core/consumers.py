import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . services import create_message, creat_chat, get_chat
from .models import SenderChoice
import uuid


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content):
        payload = {
            "message_uuid": str(uuid.uuid4()),
            "chat_id": content["chat_id"],
            "text": content["text"],
            "sender": content["sender"]
        }

        await self.send_json({
            "status": "queued",
            "message_uuid": payload["message_uuid"]
        })