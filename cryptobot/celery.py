from __future__ import absolute_import
import os

from django.conf import settings
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cryptobot.settings")
app = Celery("ccrypto")

app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # fetch market_watcher
    sender.add_periodic_task(120.0, fetch_market_data.s(), name="fetch_market_data")
    # fetch market_watcher
    sender.add_periodic_task(300.0, fetch_social_data.s(), name="fetch_social_data")
    # run
    sender.add_periodic_task(120.0, run_executor.s(), name="run_executor")


@app.task()
def fetch_market_data():
    from crypto import tasks

    tasks.fetch_market_data()


@app.task()
def fetch_social_data():
    from crypto import tasks

    tasks.fetch_social_data()


@app.task()
def run_executor():
    from crypto import tasks

    tasks.run_executor()
