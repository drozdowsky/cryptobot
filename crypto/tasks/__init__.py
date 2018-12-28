from celery.utils.log import get_task_logger

from crypto.crypto_task import run

LOGGER = get_task_logger(__name__)


def fetch_and_send():
    run(LOGGER)
