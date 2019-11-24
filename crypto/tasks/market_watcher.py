from decimal import Decimal
from functools import reduce

from django.utils import timezone

from crypto.market.api import BitBay
from crypto.models import get_or_create_crypto_model, MarketHistoric


def run_market_watcher_task(logger):
    # FIXME: crypto_hardcoded
    # FIXME: currency_hardocded
    try:
        crypto_model = get_or_create_crypto_model("Ethereum", "ETH")
        bb = BitBay("ETH", "PLN")
        bid_val, ask_val = bb.bids_value, bb.asks_value
        transaction_value = bb.transaction_value / 50
        last = Decimal(bb.last)

        mh = MarketHistoric(
            crypto=crypto_model,
            price=last,
            bids_value=bid_val,
            asks_value=ask_val,
            avg_transaction_value=transaction_value,
            response_json=bb.json,
        )
        # datetime = auto_now_add = True
        mh.save()
    except Exception as ex:
        logger.error("[MWT] {ex}.".format(ex=str(ex)))
        return None

    return mh


class MarketWatcherParser:
    def __init__(self, mh, logger):
        """
        :param mh: market historic
        """
        self.mh = mh
        self.logger = logger

    def get_last_value(self):
        return self.mh.price

    def get_ratio_bids_asks(self):
        try:
            ratio = self.mh.bids_value / self.mh.asks_value
        except ZeroDivisionError:
            raise Exception("Division by zero in market_watcher")
        else:
            return ratio

    def get_ratio_bids_asks_pow(self):
        return self.get_ratio_bids_asks() ** 0.25  # FIXME: hardcoded_constant

    def get_value_from_past(self, _timedelta):
        try:
            crypto = MarketHistoric.objects.filter(
                date__gte=timezone.now() - _timedelta - timezone.timedelta(minutes=5),
                date__lte=timezone.now() - _timedelta,
            ).latest("date")
        except Exception as e:
            value = self.get_last_value()
            self.logger.warning(
                "get_value_from_past [E]: {} - returning {} ({})".format(
                    str(e), value, str(_timedelta)
                )
            )
            return value
        else:
            return crypto.price

    def get_ratio_from_past(self, _timedelta):
        _past = float(self.get_value_from_past(_timedelta))
        _now = float(self.get_last_value())
        return ((_now - _past) / _past) * 100

    def get_ratio_multiplier(self, divider=22, **timedelta):
        return 1 / max(
            min(
                1
                + (self.get_ratio_from_past(timezone.timedelta(**timedelta)) / divider),
                2.0,
            ),
            0.5,
        )

    def get_market_bot_multiplier(self):
        market_bot_value = reduce(
            lambda x, y: x * y,
            [
                self.get_ratio_bids_asks_pow(),
                self.get_ratio_multiplier(22, days=7),
                self.get_ratio_multiplier(16, days=1),
            ],
        )
        return min(0, max(2, market_bot_value))

    def process_crypto(self):
        return {
            "Ratio from 1h ago": self.get_ratio_multiplier(
                12, hours=7
            ),  # FIXME: hardcoded_constant - 12
            "Ratio from 24h ago:": self.get_ratio_multiplier(
                16, days=1
            ),  # FIXME: hardcoded_constant - 16
            "Ratio from 7d ago": self.get_ratio_multiplier(
                22, days=7
            ),  # FIXME: hardcoded_constant - 22
            "Ratio bid/ask pow": self.get_ratio_bids_asks_pow(),
            "Crypto multiplier": self.get_market_bot_multiplier(),
        }

    # ideas
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
