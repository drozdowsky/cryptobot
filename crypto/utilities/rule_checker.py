from django.utils import timezone

from crypto.models import Trade


class RuleChecker(object):
    def __init__(self, market_parser, social_parser, crypto, ruleset):
        self.mp = market_parser
        self.sp = social_parser
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
        return rule.value < float(self.mp.get_last_value())

    def get_above(self, rule):
        return rule.value > float(self.mp.get_last_value())

    def get_change_above(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        if float(rule.price - latest_trade.price) > rule.value:
            return True

        return False

    def get_change_below(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        if float(self.mp.get_latest_value() - latest_trade.price) < rule.value:
            return True

        return False

    def get_change_perc_above(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _price = self.mp.get_latest_value()
        if (float(_price - latest_trade.price) / float(_price)) * 100 > rule.value:
            return True

        return False

    def get_change_perc_below(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _price = self.mp.get_latest_value()
        if (float(_price - latest_trade.price) / float(_price)) * 100 < rule.value:
            return True

        return False

    def get_max_value_perc(self, rule):
        return rule.value

    def get_max_value(self, rule):
        return rule.value

    def get_after_minutes(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        if (timezone.now() - latest_trade.date).seconds // 60 >= rule.value:
            return True

        return False

    def _get_latest_trade(self, rule):
        if not self._latest_trade:
            self._latest_trade = Trade.objects.filter(rule_set=rule.rule_set).latest()

        if not self._latest_trade:
            self._latest_trade = Trade.objects.create(rule_set=self.ruleset,
                                                      type_of_trade='E',
                                                      price=self.mp.get_latest_value(),
                                                      crypto=self.crypto)

        return self._latest_trade

    def get_market_bot_above(self, rule):
        return self.mp.get_market_bot_multiplier() > rule.value

    def get_market_bot_below(self, rule):
        return self.mp.get_market_bot_multiplier() < rule.value

    def get_social_bot_above(self, rule):
        return self.sp.get_social_bot_multiplier() > rule.value

    def get_social_bot_below(self, rule):
        return self.sp.get_social_bot_multiplier() < rule.value
