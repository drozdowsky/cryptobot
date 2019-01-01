from crypto.utilities import RuleChecker
from crypto.models import RuleSet, get_or_create_crypto_model


def run_executor_task(logger, mh, sh):
    # FIXME: hardcoded_crypto
    crypto_model = get_or_create_crypto_model('Ethereum', 'ETH')
    Executor(mh, sh, crypto_model, logger).run()


class Executor(object):
    def __init__(self, market_hist, social_hist, crypto, logger):
        self.mh = market_hist
        self.sh = social_hist
        self.crypto = crypto
        self.logger = logger

    def run(self):
        qs = RuleSet.objects.filter(crypto=self.crypto) \
            .select_related('owner', 'rules')

        for rs in qs:
            rc = RuleChecker(self.mh, self.sh, self.crypto, rs)
            try:
                _result = rc.run()
            except Exception as ex:
               self.logger.warning(str(ex))
            else:
                if _result:
                    self.process_result(_result)

    def process_result(self, result):
        pass
