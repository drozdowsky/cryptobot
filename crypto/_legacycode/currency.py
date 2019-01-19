import datetime

from .models import CryptocurrencyCache, Cryptocurrency
from .market.response import ServerUnavailable


class DowntimeException(Exception):
    pass


class Currency(object):
    def __init__(self, crypto, currency_short, percent, market_instance, update_time_in_minutes):

        self.crypto = crypto

        self.market = market_instance

        self.percent = 0.0
        self.min_percent = percent

        self.currency_short = currency_short

        self.min_update_time = update_time_in_minutes

        self.last_update = datetime.datetime.now()
        self.value = -1
        self.cached = None
        self.crypto_instance = None

    def set_up_and_get_crypto_fever(self):
        try:
            self.value = self.market.last
        except ServerUnavailable:
            raise DowntimeException

        if self.value <= 0:
            raise DowntimeException

        self.crypto_instance = Cryptocurrency.objects.create(crypto=self.crypto, value=self.value)
        self.cached, created = CryptocurrencyCache.objects.get_or_create(crypto=self.crypto)

        if created:
            self.cached.value = self.value
            self.cached.save()

        return self.crypto_instance

    def get_current_update_percent(self):
        self.percent = self.get_percent()

    def __str__(self):
        return '{0}: {1}{2} ({3:+.2f}%)'.format(self.crypto.short_name, self.value, self.currency_short, self.percent)

    def get_percent(self):
        return ((self.value-self.cached.value)/max(1, self.cached.value)) * 100.0

    def generate_title_body_list(self):
        title_list = []

        body_list = [
            '<b>{}</b>:'.format(str.upper(self.crypto.long_name)),

            '{0} price: {1} {2} [{3:+.2f} %]'.format(
                self.crypto.long_name, self.value, self.currency_short, self.percent
            ),

            'From <b>{}</b> to <b>{}</b>:'.format(
                str(self.cached.last_update.replace(microsecond=0)), str(datetime.datetime.now().replace(microsecond=0))
            ),
        ]

        if abs(self.percent) >= self.min_percent:
            title_list.append(self.__str__())

        # TODO: Add Hit the Highest and the lowest value in 24h
        '''
        if self.get_percent(self.last, self.value) >= 1:
            if self.min > self.value:
                title_list.append('{} hit lowest 24h'.format(self.short_name))
                body_list.append('{} hit the lowest value in 24h'.format(self.long_name))

            elif self.max < self.value:
                title_list.append('{} hit highest 24h'.format(self.short_name))
                body_list.append('{} hit the highest value in 24h'.format(self.long_name))
        '''

        return title_list, body_list

    def generate_mail_lists(self):
        if self.crypto_instance is None:
            self.set_up_and_get_crypto_fever()

        self.get_current_update_percent()

        title, body = self.generate_title_body_list()

        if (datetime.datetime.now()-self.cached.last_update).total_seconds()//60 >= self.min_update_time > 0 \
                and self.percent >= 1:

            title.append(self.__str__())

        if len(title):
            self.update()

        return title, body

    def update(self):
        self.cached.value = self.value
        self.cached.save()
