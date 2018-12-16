from test_plus.test import TestCase
from decimal import Decimal
from datetime import timedelta

from .bot import BotBase, NotEnoughCrypto, NotEnoughMoney


class BotTests(TestCase):
    def setUp(self):
        self.bot = BotBase('testing', None, 'Ethereum', 'ETH')
        self.bot.init_bot(2.5, 1000.0)

    def test_fail_buy(self):
        with self.assertRaises(NotEnoughMoney):
            self.bot.buy(1.0, 1001)

    def test_fail_sell(self):
        with self.assertRaises(NotEnoughCrypto):
            self.bot.sell(2.6, 1001)

    def test_pass_buy_sold(self):
        self.bot.buy(0.5, 500.0)        # 3.00, 750.0
        self.bot.sell(0.20, 100.0)      # 2.80, 770.0
        self.bot.buy(0.5, 500.0)        # 3.30, 520.0

        self.assertEqual(self.bot.get_in_crypto_value(), Decimal('3.30'))
        self.assertEqual(self.bot.get_in_currency_value(), Decimal('520.0'))

    def test_withdraw_crypto(self):
        self.bot.withdraw_crypto(2.0)
        self.assertEqual(self.bot.get_in_crypto_value(), Decimal('0.5'))

    def test_withdraw_money(self):
        self.bot.withdraw_currency(1000.0)
        self.assertEqual(self.bot.get_in_currency_value(), Decimal('0.0'))

    def test_withdraw_fail(self):
        with self.assertRaises(NotEnoughCrypto):
            self.bot.withdraw_crypto(2.51)

    def test_withdraw_fail_2(self):
        with self.assertRaises(NotEnoughMoney):
            self.bot.withdraw_currency(1000.01)

    def test_sorting_dates(self):
        trades = [self.bot.buy(1, 100), self.bot.buy(1, 101), self.bot.buy(1, 102)]

        for i, t in enumerate(trades):
            t.date += timedelta(minutes=i)
            t.save()

        self.assertEqual(list(self.bot.get_trades_and_withdraws()), trades)
        self.assertEqual(list(self.bot.get_trades_and_withdraws())[1].date, trades[1].date)

    def test_reliable_bids(self):
        trades = [self.bot.buy(1, 100), self.bot.buy(1, 101), self.bot.buy(1, 102)]

        self.bot.sell(0.05, 50)

        trades.append(self.bot.buy(0.1, 103))

        self.assertEqual(list(self.bot.get_reliable_bid_trades()), trades)

    def test_get_value_bids_past_present(self):
        self.bot.buy(1, 100)
        self.bot.buy(1, 101)
        self.bot.buy(1, 102)
        self.bot.sell(0.05, 100)
        self.bot.buy(0.02, 0)

        self.assertEqual(self.bot.get_value_of_reliable_bid_trades(), Decimal(100+101+102))
        self.assertEqual(self.bot.get_real_value_of_reliable_bid_trades(100), Decimal(302))
