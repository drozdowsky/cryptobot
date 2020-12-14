from unittest.mock import Mock

from crypto.tasks.market_watcher import MarketWatcherParser
from crypto.tasks.social_watcher import SocialWatcherParser
from crypto.utilities.mailing import MailGenerator
from crypto.tests import *
from crypto.utilities.rule_checker import RuleChecker
from crypto.models import MarketHistoric

from django.utils import timezone
from datetime import timedelta


class MailingTest(BaseTest):
    def setUp(self):
        self.cryptoSetUp()

        self.mp = MarketWatcherParser(self.mh, LOGGER)
        self.sp = SocialWatcherParser(self.sh, LOGGER)
        self.past_price = MarketHistoric.objects.create(
            crypto=self.crypto,
            bids_value=200.0,
            asks_value=200.0,
            avg_transaction_value=200.0,
            price=Decimal("200.0"),
            response_json={},
            date=self.mh.date - timedelta(hours=24),
        )
        self.rc = RuleChecker(self.mp, self.sp, self.crypto, self.ruleset)

    def test_past_price(self):
        mg = MailGenerator(
            self.crypto, self.ruleset, self.mp, self.sp, {}, self.past_price, Mock()
        )
        title = mg.generate_mail()[0]
        assert title == ["[E: ETH]", "Test ruleset", "[24h/+60.00 %]"]
