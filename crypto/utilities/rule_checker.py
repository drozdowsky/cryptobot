from django.utils import timezone

from crypto.models import Trade


class RuleChecker(object):
    def __init__(self, market_historic, social_historic, crypto, ruleset):
        self.mh = market_historic
        self.sh = social_historic
        self.crypto = crypto
        self.ruleset = ruleset
        self.user = ruleset.owner
        self._latest_trade = None  # store latest trade for this ruleset

    def run(self):
        results = {}

        for rule in self.ruleset.rules.all():
            tof = rule.RULE_TYPES_DICT.get(rule.type_of_rule, None)
            _func = getattr(self, 'get_' + str(tof), None)
            if _func:
                _result = _func()
                if not _result:
                    return {}
                results[rule.type_of_rule] = _result
            else:
                raise Exception("Rule {} does not exist!".format(rule.type_of_rule))

        return results

    def get_below(self, rule):
        return rule.value < float(self.mh.price)

    def get_above(self, rule):
        return rule.value > float(self.mh.price)

    def get_change_above(self, rule):
        latest_trade = self._get_latest_trade(self.mh)
        if float(rule.price - latest_trade.price) > rule.value:
            return True

        return False

    def get_change_below(self, rule):
        latest_trade = self._get_latest_trade(self.mh)
        if float(self.mh.price - latest_trade.price) < rule.value:
            return True

        return False

    def get_change_perc_above(self, rule):
        latest_trade = self._get_latest_trade(self.mh)
        if (float(self.mh.price - latest_trade.price) / float(self.mh.price)) * 100 > rule.value:
            return True

        return False

    def get_change_perc_below(self, rule):
        latest_trade = self._get_latest_trade(self.mh)
        if (float(self.mh.price - latest_trade.price) / float(self.mh.price)) * 100 < rule.value:
            return True

        return False

    def get_max_value_perc(self, rule):
        return rule.value

    def get_max_value(self, rule):
        return rule.value

    def get_after_minutes(self, rule):
        latest_trade = self._get_latest_trade(self.mh)
        if (timezone.now() - latest_trade.date).seconds // 60 >= rule.value:
            return True

        return False

    def _get_latest_trade(self, rule):
        if not self._latest_trade:
            self._latest_trade = Trade.objects.filter(rule_set=rule.rule_set).latest()

        if not self._latest_trade:
            self._latest_trade = Trade.objects.create(rule_set=self.ruleset,
                                                      type_of_trade='E',
                                                      price=self.mh.price,
                                                      crypto=self.crypto)

        return self._latest_trade
