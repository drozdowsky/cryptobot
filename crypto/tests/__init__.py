from decimal import Decimal
from logging import getLogger

from django.conf import settings
from django.contrib.auth import get_user_model
from test_plus.test import TestCase

from crypto.models import *

LOGGER = getLogger("crypto_tests")


class BaseTest(TestCase):
    def cryptoSetUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser", password="12345"
        )
        self.crypto = get_or_create_crypto_model(short_name="ETH", long_name="Ethereum")
        self.mh = MarketHistoric.objects.create(
            crypto=self.crypto,
            bids_value=500.0,
            asks_value=500.0,
            avg_transaction_value=500.0,
            price=Decimal("500.0"),
            response_json={},
        )

        self.sh = SocialHistoric.objects.create(
            crypto=self.crypto,
            gtrends_top_7d=1.0,
        )

        self.ruleset = RuleSet.objects.create(
            name="Test ruleset",
            crypto=self.crypto,
            owner=self.user,
            type_of_ruleset="E",
        )
