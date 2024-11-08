import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('backend-challenge')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)

app.autodiscover_tasks()
