from celery.utils.log import get_task_logger

from crypto.tasks import market_watcher, social_watcher, executor

LOGGER = get_task_logger(__name__)


def fetch_and_send():
    _mh = market_watcher.run_market_watcher_task(LOGGER)
    if _mh:
        pass
        #run(LOGGER)


def fetch_social_data():
    social_watcher.run_social_watcher_task(LOGGER)
