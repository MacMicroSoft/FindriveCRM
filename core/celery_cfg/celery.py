import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "findrive_crm.settings")
app = Celery("core.celery_cfg")

app.config_from_object("findrive_crm.settings", namespace="CELERY")
app.autodiscover_tasks()