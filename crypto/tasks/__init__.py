from celery.utils.log import get_task_logger
from datetime import timedelta
from django.utils import timezone

from crypto.tasks import market_watcher, social_watcher, executor
from crypto.models import MarketHistoric, SocialHistoric

LOGGER = get_task_logger(__name__)


def fetch_market_data():
    market_watcher.run_market_watcher_task(LOGGER)


def fetch_social_data():
    social_watcher.run_social_watcher_task(LOGGER)


def run_executor():
    mh = MarketHistoric.objects.latest('date')

    if not mh or mh.date+timedelta(minutes=5) < timezone.now():
        LOGGER.error("run_executor: no recent MarketHistoric, task did not started")
        return 1

    sh = SocialHistoric.objects.latest('date')

    if not sh or sh.date+timedelta(minutes=10) < timezone.now():
        LOGGER.error("run_executor: no recent SocialHistoric, task did not started")
        return 2

    mp = market_watcher.MarketWatcherParser(mh, LOGGER)
    sp = social_watcher.SocialWatcherParser(sh, LOGGER)
    executor.run_executor_task(LOGGER, mp, sp)


def run_ghetto_way():
    from time import sleep
    while True:
        try:
            fetch_market_data()
            fetch_social_data()
            run_executor()
            sleep(60)
        except Exception as ex:
            print('run_ghetto_way: {ex}'.format(ex=str(ex)))
