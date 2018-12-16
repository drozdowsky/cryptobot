from celery.utils.log import get_task_logger

from .crypto_task import run

logger = get_task_logger(__name__)


def fetch_and_send():
    run(logger)
