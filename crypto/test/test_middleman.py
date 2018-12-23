from test_plus.test import TestCase
from decimal import Decimal
from django.utils import timezone

from .middleman.middleman import Middleman
from .bot import BotBase
from .models import get_or_create_crypto_model, Cryptocurrency


class MidlemanTests(TestCase):
    def always_return_1000(self):
        return 1000

    def setUp(self):
        self.crypto = get_or_create_crypto_model('Ethereum', 'ETH')
        self.bot = BotBase('TestBot', self.crypto)
        self.middleman = Middleman(None, None, self.bot, self.crypto)
        self.middleman.get_last_value = self.always_return_1000

        c = Cryptocurrency.objects.create(crypto=self.crypto, value=2000)
        c.date = timezone.now() - timezone.timedelta(days=1)
        c.save()

        c = Cryptocurrency.objects.create(crypto=self.crypto, value=100)
        c.date = timezone.now() - timezone.timedelta(days=4)
        c.save()

        c = Cryptocurrency.objects.create(crypto=self.crypto, value=1000)
        c.date = timezone.now() - timezone.timedelta(days=7)
        c.save()

    def test_get_ratio_multiplier(self):
        self.assertEqual(self.middleman.get_ratio_multiplier(50, days=1), 2.0)
        self.assertEqual(self.middleman.get_ratio_multiplier(1, days=7), 1.0)
        self.assertEqual(self.middleman.get_ratio_multiplier(1, days=4), 0.5)
