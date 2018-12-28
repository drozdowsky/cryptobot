import logging
from decimal import Decimal
from .models import Trade, CryptoModel


logger = logging.getLogger('CRYPTO.BOT')


class NotEnoughMoney(Exception):
    pass


class NotEnoughCrypto(Exception):
    pass


class NotLoaded(Exception):
    pass


class BotBase:
    def __init__(self, name, crypto=None, long_crypto_name=None, short_crypto_name=None):
        self.name = name
        self.crypto_value = Decimal(0)
        self.currency_value = Decimal(0)
        self.short_crypto_name = short_crypto_name
        self.long_crypto_name = long_crypto_name
        self.loaded = False
        self.bot_model = None
        self.trades = []
        self.crypto = crypto

    def buy(self, amount, price):
        """
        Buy crypto
        """
        self.is_loaded()
        amount = Decimal(str(amount))
        price = Decimal(str(price))

        if amount*price > self.currency_value:
            raise NotEnoughMoney

        self.crypto_value += amount
        self.currency_value -= amount*price
        self.trades.append(Trade.objects.create(type_of_trade='Buy', amount=amount, price=price, bot=self.bot_model,
                                                crypto=self.crypto))
        self.save_data()
        return self.trades[-1]

    def sell(self, amount, price):
        """
        Sell crypto
        """
        self.is_loaded()

        amount = Decimal(str(amount))
        price = Decimal(str(price))

        if amount > self.crypto_value:
            raise NotEnoughCrypto

        self.crypto_value -= amount
        self.currency_value += amount*price
        self.trades.append(Trade.objects.create(type_of_trade='Sell', amount=amount, price=price, bot=self.bot_model,
                                                crypto=self.crypto))
        self.save_data()
        return self.trades[-1]

    def withdraw_crypto(self, amount):
        """
        Withdraw crypto
        """
        self.is_loaded()

        amount = Decimal(str(amount))

        if amount > self.crypto_value:
            raise NotEnoughCrypto

        self.crypto_value -= amount
        t = Trade.objects.create(type_of_trade='Withdraw', amount=amount, price=0, bot=self.bot_model, crypto=self.crypto)
        self.save_data()
        return t

    def withdraw_currency(self, currency):
        self.is_loaded()

        currency = Decimal(str(currency))

        if currency > self.currency_value:
            raise NotEnoughMoney

        self.currency_value -= currency
        t = Trade.objects.create(type_of_trade='Withdraw', amount=0, price=currency, bot=self.bot_model, crypto=self.crypto)
        self.save_data()
        return t

    def init_bot(self, crypto_value, currency_value):
        self.crypto_value = Decimal(str(crypto_value))
        self.currency_value = Decimal(str(currency_value))

        if not self.load_data():
            logger.warning('init_bot: Bot already exist! Loaded existing bot with his data (crypto, currency)')

    def load_data(self):
        if self.crypto is None:
            self.crypto, _ = CryptoModel.objects.get_or_create(short_name=self.short_crypto_name,
                                                               long_name=self.long_crypto_name)

        self.bot_model, created = Bot.objects.get_or_create(name=self.name)

        if created:
            self.bot_model.crypto = self.crypto
            self.bot_model.crypto_value = self.crypto_value
            self.bot_model.currency_value = self.currency_value
            self.bot_model.save()
        else:
            self.trades = list(self.bot_model.trades.exclude(type_of_trade='Withdraw').order_by('date'))
            self.crypto_value = self.bot_model.crypto_value
            self.currency_value = self.bot_model.currency_value

        self.loaded = True
        return created

    def save_data(self):
        if not self.loaded:
            raise NotLoaded

        self.bot_model.save()

    def get_in_crypto_value(self):
        self.is_loaded()
        return self.crypto_value

    def get_in_currency_value(self):
        self.is_loaded()
        return self.currency_value

    def get_trades(self):
        self.is_loaded()
        return self.trades

    def get_trades_and_withdraws(self):
        self.is_loaded()
        return self.bot_model.trades.all().order_by('date')

    def get_reliable_bid_trades(self):
        """
        Lets say we have 5 ETH, this function will return list of last bid trades that sum up to 5 ETH
        :return: reliable trade list
        """
        self.is_loaded()
        current_value = 0
        trade_list = []
        _max = self.get_in_crypto_value()+Decimal('0.1')

        for trade in self.trades[::-1]:
            if trade.type_of_trade != 'Buy':
                continue

            if current_value < _max:
                current_value += trade.amount
                trade_list.append(trade)

        return trade_list[::-1]

    def get_value_of_reliable_bid_trades(self):
        """
        The value of get_reliable_bid_trades but not in present time but when the crypto were bought
        :return:
        """
        _value = 0
        trade_list = self.get_reliable_bid_trades()

        for trade in trade_list:
            _value += trade.amount*trade.price

        return _value

    def get_real_value_of_reliable_bid_trades(self, current_price_of_crypto):
        """
        The value of get_reliable_bid_trades (present time)
        :return:
        """
        _value = 0
        trade_list = self.get_reliable_bid_trades()

        for trade in trade_list:
            _value += trade.amount*current_price_of_crypto

        return _value

    def get_ratio_of_reliable_bid_trades(self, current_price_of_crypto):
        return self.get_real_value_of_reliable_bid_trades(current_price_of_crypto)/self.get_value_of_reliable_bid_trades()

    def is_loaded(self):
        if not self.loaded:
            self.load_data()
