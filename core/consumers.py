import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from . services import create_message, creat_chat, get_chat
from .models import SenderChoice


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print('[SYS] - Is connected')
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_id_group = f"chat_{self.chat_id}"

        async_to_sync(self.channel_layer.group_add)(self.chat_id_group, self.channel_name)

        self.accept()


    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.chat_id_group, self.channel_name)


    def receive(self, text_data):
        context = {'type': 'chat.message'}
        print(text_data)
        received_data: dict = json.loads(text_data)
        sender = received_data.get('sender').lower()
        context['sender'] = sender
        chat = creat_chat(
            chat_id = received_data.get('chat_id'),
            user_first = received_data.get('first_name'),
            user_last = received_data.get('last_name'),
            tagname = received_data.get('username')
        )
        if chat is None:
            chat = get_chat(received_data.get('chat_id'))

        new_message = create_message(
            chat = chat,
            message = received_data.get('message'),
            from_ = received_data.get('sender').lower(),
            is_recived=True
        )
        context['message'] = new_message

        async_to_sync(self.channel_layer.group_send)(self.chat_id_group, context)


    def chat_message(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}))