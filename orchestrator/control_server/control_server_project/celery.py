import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "control_server_project.settings")
app = Celery("control_server_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()