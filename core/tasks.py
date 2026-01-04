from celery import shared_task
from .models import Chat, Message, SenderChoice
from django.db import transaction
from time import sleep


@shared_task(bind=True, retry_backoff=5, name='web_to_tg', queue='web_to_tg')
def handle_ws_message(self, payload: dict):
    with transaction.atomic():
        chat = Chat.objects.select_for_update().get(
            tg_chat_id=payload["chat_id"]
        )

        msg = Message.objects.get_or_create(
            uuid=payload["message_uuid"],
            defaults={
                "chat": chat,
                "sender": SenderChoice(payload["sender"]),
                "message": payload["text"],
            }
        )

        return