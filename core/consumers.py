import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from . services import create_message, creat_chat, get_chat
from .models import SenderChoice
from .tasks import handle_ws_message
import uuid
import asyncio
import aio_pika


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content):
        payload = {
            "message_uuid": str(uuid.uuid4()),
            "chat_id": content["chat_id"],
            "text": content["text"],
            "sender": content["sender"]
        }
        await asyncio.sleep(5)
        handle_ws_message.delay(payload)

        await self.send_json({
            "status": "queued",
            "message_uuid": payload["message_uuid"]
        })


async def web_rabbit_listener():
    while True:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
        queue_name = "tg_to_web"

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = message.body.decode()
                        data = json.loads(payload)[0][0]
                        print(payload)

asyncio.run(web_rabbit_listener())