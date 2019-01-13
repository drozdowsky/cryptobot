import logging
import time
from datetime import datetime

from crypto.market.response import Request, ServerUnavailable

logger = logging.getLogger('MARKET.API')


class Market:
    def __init__(self, url):
        self.url = url
        self._json = None
        self._bids_value = -1
        self._asks_value = -1
        self._transaction_value = -1
        self._last = -1
        self._evaluated = False

    def _get_json(self):
        return Request(self.url).get_json()

    def _parse_json(self):
        while True:
            try:
                self._json = self._get_json()
            except ServerUnavailable:
                logger.warning('Server unavailable!')
                raise
            else:
                break

    @property
    def json(self):
        if self._json is None:
            self._parse_json()

        return self._json

    def get_value_of(self, _type, _limit=None, significance=True):
        """
        :param _type: 'asks' / 'bids'
        :param _limit: int - limit to x results - if none all will be included
        :param significance: if True the last one will have 0 priority the first 1, the second 99% etc...
        :return: value of
        """

        _abs = self.json.get(_type, None)
        if _abs is None or type(_abs) is not list:
            raise ProcessLookupError

        len_abs = _limit if _limit else len(_abs)
        value = 0

        for i, ab in enumerate(_abs[:len_abs]):
            value += ab[0] * ab[1] * (((len_abs-i)/len_abs) if significance else 1)

        return value

    @property
    def bids_value(self):
        self.try_evaluate()
        return self._bids_value

    @property
    def asks_value(self):
        self.try_evaluate()
        return self._asks_value

    @property
    def transaction_value(self):
        self.try_evaluate()
        return self._transaction_value

    @property
    def last(self):
        return self.json.get('last', -1)

    def try_evaluate(self):
        if self._evaluated is False:
            self.evaluate_calculations()
            self._evaluated = True

    def evaluate_calculations(self):
        raise NotImplementedError


class BitBay(Market):
    def __init__(self, crypto, currency, *args, **kwargs):
        url = 'https://bitbay.net/API/Public/{crypto}{real}/all.json?sort=desc'.format(crypto=crypto, real=currency)
        super(BitBay, self).__init__(url)

    def get_value_of_bids(self, limit=None):
        """
        Get Value of bids on market (better = higher priority)
        :param limit: limit to X bids, if None - all will be included
        :return: value of bids (not real!)
        """
        self._bids_value = self.get_value_of('bids', limit)
        return self._bids_value

    def get_value_of_asks(self, limit=None):
        """
        Get Value of asks on market (better = higher priority)
        :param limit: limit to X bids, if None - all will be included
        :return: value of asks (not real!)
        """
        self._asks_value = self.get_value_of('asks', limit)
        return self._asks_value

    def get_last_50_transactions_value(self, date_limit=None):
        """
        Get sum of last (max) 50 transactions
        :param date_limit: datetime object to filter with (only greater than)
        :return: sum of last transactions in currency (USD/PLN/...) [max 50]
        """
        trans = self.json.get('transactions', None)
        if trans is None or type(trans) is not list:
            raise ProcessLookupError(type(trans))

        value = 0

        for t in trans:
            if date_limit and datetime.fromtimestamp(t['date']) < date_limit:
                continue

            value += t['price']*t['amount']

        self._transaction_value = value
        return value

    def evaluate_calculations(self):
        self.get_value_of_asks()
        self.get_value_of_bids()
        self.get_last_50_transactions_value()


def main():
    bb = BitBay('ETH', 'PLN')
    print(bb.bids_value/bb.asks_value, bb.bids_value, bb.asks_value, bb.transaction_value/50, bb.last)


if __name__ == '__main__':
    main()
