from celery import Celery


celery_app = Celery(
    "django_project",
    broker="amqp://guest:guest@localhost:5672//",  # RabbitMQ
    backend="rpc://"
)
celery_app.autodiscover_tasks()