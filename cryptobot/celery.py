from __future__ import absolute_import
import os

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cryptobot.settings')
app = Celery('ccrypto')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(120.0, fetch_and_send.s(), name='fetch_and_send')


@app.task()
def fetch_and_send():
    from crypto import tasks
    tasks.fetch_and_send()
