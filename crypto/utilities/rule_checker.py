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
                _result = _func(rule)
                if _result is False:
                    return {}
                results[rule.type_of_rule] = _result
            else:
                raise Exception("Rule {} does not exist!".format(rule.type_of_rule))

        return results

    def get_below(self, rule):
        _last_value = float(self.mp.get_last_value())
        if rule.value > _last_value:
            return _last_value

        return False

    def get_above(self, rule):
        _last_value = float(self.mp.get_last_value())
        if rule.value < _last_value:
            return _last_value

        return False

    def get_change_above(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _difference = float(self.mp.get_latest_value() - latest_trade.price)
        if _difference > rule.value:
            return _difference

        return False

    def get_change_below(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _difference = float(self.mp.get_latest_value() - latest_trade.price)
        if _difference < rule.value:
            return _difference

        return False

    def get_change_perc_above(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _price = self.mp.get_latest_value()
        _perc = (float(_price - latest_trade.price) / float(_price)) * 100
        if _perc > rule.value:
            return _perc

        return False

    def get_change_perc_below(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        _price = self.mp.get_latest_value()
        _perc = (float(_price - latest_trade.price) / float(_price)) * 100
        if _perc < rule.value:
            return _perc

        return False

    def get_max_value_perc(self, rule):
        # FIXME: not_implemented
        return rule.value

    def get_max_value(self, rule):
        # FIXME: not_implemented
        return rule.value

    def get_after_minutes(self, rule):
        latest_trade = self._get_latest_trade(self.mp.mh)
        if (timezone.now() - latest_trade.date).total_seconds() >= rule.value * 60:
            return latest_trade.date

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
        _market_multiplier = self.mp.get_market_bot_multiplier()
        if _market_multiplier > rule.value:
            return _market_multiplier

        return False

    def get_market_bot_below(self, rule):
        _market_multiplier = self.mp.get_market_bot_multiplier()
        if _market_multiplier < rule.value:
            return _market_multiplier

        return False

    def get_social_bot_above(self, rule):
        _social_multiplier = self.sp.get_social_bot_multiplier()
        if _social_multiplier > rule.value:
            return _social_multiplier

        return False

    def get_social_bot_below(self, rule):
        _social_multiplier = self.sp.get_social_bot_multiplier()
        if _social_multiplier < rule.value:
            return _social_multiplier

        return False
