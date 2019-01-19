from crypto.trends.google import get_crypto_trend_ratio

from crypto.models import get_or_create_crypto_model, SocialHistoric


def run_social_watcher_task(logger):
    # FIXME: crypto_hardcoded
    try:
        crypto_model = get_or_create_crypto_model('Ethereum', 'ETH')
        gtrends_7day = get_crypto_trend_ratio(crypto_model, 7)
        sh = SocialHistoric(crypto=crypto_model,
                            gtrends_top_7d=gtrends_7day)
        # datetime = auto_now_add = True
        sh.save()
    except Exception as ex:
        logger.error('[SWT] {ex}.'.format(ex=str(ex)))
        return None

    return sh


class SocialWatcherParser:
    def __init__(self, sh, logger):
        """
        :param mh: social historic
        """
        self.sh = sh
        self.logger = logger

    def get_social_bot_multiplier(self):
        return self.sh.gtrends_top_7d
