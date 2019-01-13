from datetime import timedelta

from crypto.models import MarketHistoric, RuleSet, Trade, \
    get_or_create_crypto_model
from crypto.utilities.mailing import MailGenerator
from crypto.utilities.rule_checker import RuleChecker

from django.utils import timezone


def run_executor_task(logger, mp, sp):
    # FIXME: hardcoded_crypto
    crypto_model = get_or_create_crypto_model('Ethereum', 'ETH')
    Executor(mp, sp, crypto_model, logger).run()


class Executor(object):
    def __init__(self, market_parser, social_parser, crypto, logger):
        self.mp = market_parser
        self.sp = social_parser
        self.crypto = crypto
        self.logger = logger
        self.past_price = MarketHistoric.objects.filter(
            date__lte=timezone.now()-timedelta(hours=24)
        ).order_by('-date').first() or self.mp.mh.price

    def run(self):
        qs = RuleSet.objects.filter(crypto=self.crypto) \
            .select_related('owner').prefetch_related('rules')

        self.logger.info('[EXEC] Starting processing rulesets!')
        for rs in qs:
            self.logger.info('[EXEC] ruleset(%d): %s', rs.id, rs.type_of_ruleset)
            rc = RuleChecker(self.mp, self.sp, self.crypto, rs)
            try:
                _result = rc.run()
            except Exception as ex:
               self.logger.warning(str(ex))
            else:
                if _result:
                    self.process_result(_result, rs)

        self.logger.info('[EXEC] Finished processing rulesets!')

    def process_result(self, result, rs):
        # FIXME: trades_here!
        type_of_ruleset = rs.type_of_ruleset
        try:
            result = MailGenerator(self.crypto, rs, self.mp, self.sp, result,
                                   self.past_price, self.logger).run()
        except Exception as ex:
            self.logger('process_result {}'.format(str(ex)))
        else:
            # exit 0 == success
            if not result:
                Trade.objects.create(type_of_trade=type_of_ruleset,
                                     price=self.mp.mh.price,
                                     rule_set=rs,
                                     crypto=self.crypto)
