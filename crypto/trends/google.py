from datetime import datetime, timedelta
from pytrends.request import TrendReq

# google trends
GT_SIGNIFICANCE = 1.4
GT_POW = 0.25


class GoogleTrends:
    TIME_MAPPING = {
        1: "now 1-d",
        7: "now 7-d",
        30: "today 1-m",
        60: "today 2-m",
        90: "today 3-m",
    }

    def __init__(self, keywords, day):
        self.keywords = keywords
        self.day = day
        self.request = TrendReq()

    def get_interest(self):
        try:
            date_format = self.TIME_MAPPING[self.day]
        except KeyError:
            date_format = "{} {}".format(
                datetime.now().strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=self.day)).strftime("%Y-%m-%d"),
            )

        self.request.build_payload(self.keywords, timeframe=date_format)
        return self.request.interest_over_time()


class SignificanceOfTrends:
    def __init__(self, day, crypto):
        self.day = day
        self.result = None
        self.crypto = crypto

    def build_results(self):
        self.result = GoogleTrends([self.crypto.long_name], self.day).get_interest()
        return self.result

    def get_value_for_last_results(self):
        if self.result is None:
            self.build_results()

        return self.result.values[-1][0]

    def get_value_ratio(self):
        return (self.get_value_for_last_results() / 100) * 2.0


def get_crypto_trend_ratio(crypto, day=7):
    sot = SignificanceOfTrends(day, crypto)
    return min(2, max(0, sot.get_value_ratio()))
