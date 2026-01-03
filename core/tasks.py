from celery import shared_task
from .models import Chat, Message, SenderChoice
from django.db import transaction


@shared_task
def test_task():
    print("🔥 CELERY WORKS!", flush=True)


@shared_task(bind=True, retry_backoff=5)
def handle_ws_message(self, payload: dict):
    print(f'[TASKS] -> {payload}')
    with transaction.atomic():
        chat = Chat.objects.select_for_update().get(
            tg_chat_id=payload["chat_id"]
        )

        Message.objects.get_or_create(
            uuid=payload["message_uuid"],
            defaults={
                "chat": chat,
                "sender": SenderChoice[payload["sender"]],
                "message": payload["text"],
            }
        )