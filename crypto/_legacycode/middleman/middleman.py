import logging
from decimal import Decimal
from django.utils import timezone

from crypto.market.priv_api import PrivateApiBase
from crypto.trends.google import get_crypto_trend_ratio_with_pow
from crypto.currency import DowntimeException
from crypto.models import Cryptocurrency
from crypto.constants import DIVIDER_FOR_DAY_RATIO, DIVIDER_FOR_WEEK_RATIO

logger = logging.getLogger('CRYPTO.MIDDLEMAN')


class Middleman:
    def __init__(self, private_market, public_market, bot, crypto):
        """
        :param private_market: private api market
        :param public_market:  public api
        :param bot: bot instance
        """
        self.private_market = private_market

        if self.private_market is None:
            self.private_market = PrivateApiBase()

        self.public_market = public_market
        self.bot = bot
        self.crypto = crypto
        self.crypto_ratio_pow = None

    def run(self):
        pass

    def get_last_value(self):
        return self.public_market.last

    def get_ratio_bids_asks(self):
        try:
            ratio = self.public_market.bids_value/self.public_market.asks_value
        except ZeroDivisionError:
            raise DowntimeException
        else:
            return ratio

    def get_ratio_bids_asks_pow(self):
        return self.get_ratio_bids_asks()**0.25  # FIXME: quadruple root (constant 0.25)

    def get_value_from_past(self, _timedelta):
        try:
            crypto = Cryptocurrency.objects.filter(date__gte=timezone.now()-_timedelta-timezone.timedelta(minutes=5),
                                                   date__lte=timezone.now()-_timedelta).order_by('date')[:1][0]
        except Exception as e:
            value = self.get_last_value()
            logger.warning('get_value_from_past [E]: {} - returning {}'.format(str(e), value))
            return value
        else:
            return crypto.value

    def get_ratio_from_past(self, _timedelta):
        _value = self.get_value_from_past(_timedelta)
        return ((self.get_last_value()-_value)/_value)*100

    def get_crypto_trend_ratio_pow(self):
        if self.crypto_ratio_pow is None:
            self.crypto_ratio_pow = get_crypto_trend_ratio_with_pow(self.crypto)

        return self.crypto_ratio_pow

    def get_ratio_multiplier(self, divider=22, **timedelta):
        return 1/max(min(1+(self.get_ratio_from_past(timezone.timedelta(**timedelta))/divider), 2.0), 0.5)

    def get_crypto_bot_multiplier(self):
        return self.get_crypto_trend_ratio_pow() * self.get_ratio_bids_asks_pow() \
               * self.get_ratio_multiplier(DIVIDER_FOR_WEEK_RATIO, days=7)\
               * self.get_ratio_multiplier(DIVIDER_FOR_DAY_RATIO, days=1)

    def process_crypto(self):
        return {'Crypto google trend pow': self.get_crypto_trend_ratio_pow(),
                'Ratio from 1h ago': self.get_ratio_multiplier(DIVIDER_FOR_WEEK_RATIO, hours=7),
                'Ratio from 24h ago:': self.get_ratio_multiplier(DIVIDER_FOR_WEEK_RATIO, days=1),
                'Ratio from 7d ago': self.get_ratio_multiplier(DIVIDER_FOR_WEEK_RATIO, days=7),
                'Ratio bid/ask pow': self.get_ratio_bids_asks_pow(),
                'Crypto multiplier': self.get_crypto_bot_multiplier()
                }

    # mnozenie ratio
    # 30min, 1h, 2h, 12h, 24h, 3days, 7days
    # IDEA: If crypto multiplier > 1.5 - try to sold
    #       If crypto multiplier < 0.5 - try to buy
    #
    #       Buy-sell decision making: Let's make 'class' that:
    #           # for buy decision-making lets create function that return ratio of:
                    # profit ratio (greedy %)
                    # our portfolio ratio COINS/FIAT should be 75%/25% MAX, MIN 50%/50% for crypto, (SHOULD BE SOME EXCEPTIONS FOR BIG PROFITS)
                    # AGRESSIVNESS OF BOT RATIO
