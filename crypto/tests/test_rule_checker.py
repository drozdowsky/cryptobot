from crypto.tasks.market_watcher import MarketWatcherParser
from crypto.tasks.social_watcher import SocialWatcherParser
from crypto.tests import *
from crypto.utilities.rule_checker import RuleChecker

from django.utils import timezone


class RuleCheckerEmptyTest(BaseTest):
    def setUp(self):
        self.cryptoSetUp()

        self.mp = MarketWatcherParser(self.mh, LOGGER)
        self.sp = SocialWatcherParser(self.sh, LOGGER)
        self.rc = RuleChecker(self.mp, self.sp, self.crypto, self.ruleset)

    def create_rule(self, type_of_rule, value):
        return Rule.objects.create(
            rule_set=self.ruleset,
            type_of_rule=type_of_rule,
            value=value
        )

    def create_test_type_of_rule(self, type_of_rule, val_when_true, val_when_false):
        rule = self.create_rule(type_of_rule, val_when_true)
        self.assertTrue(self.rc.run())
        rule.delete()
        rule = self.create_rule(type_of_rule, val_when_false)
        self.assertFalse(self.rc.run())
        rule.delete()

    def test_price_below(self):
        self.create_test_type_of_rule(Rule.BELOW, 501.0, 500.0)

    def test_price_above(self):
        self.create_test_type_of_rule(Rule.ABOVE, 409.0, 500.0)

    def test_empty_change_above(self):
        self.create_test_type_of_rule(Rule.CHANGE_ABOVE, -0.1, 0.0)

    def test_empty_change_below(self):
        self.create_test_type_of_rule(Rule.CHANGE_BELOW, 1.0, 0.0)

    def test_empty_perc_change_above(self):
        self.create_test_type_of_rule(Rule.CHANGE_PERC_ABOVE, -0.1, 0.0)

    def test_empty_perc_change_below(self):
        self.create_test_type_of_rule(Rule.CHANGE_PERC_BELOW, 0.1, 0.0)

    def test_after_minutes(self):
        self.create_test_type_of_rule(Rule.AFTER_MINUTES, 0.0, 1.0)

    def test_market_bot_below(self):
        self.create_test_type_of_rule(Rule.MBOT_BELOW, 1.1, 1.0)

    def test_market_bot_above(self):
        self.create_test_type_of_rule(Rule.MBOT_ABOVE, 0.9, 1.0)

    def test_social_bot_below(self):
        self.create_test_type_of_rule(Rule.SBOT_BELOW, 1.1, 1.0)

    def test_social_bot_above(self):
        self.create_test_type_of_rule(Rule.SBOT_ABOVE, 0.9, 1.0)


class RuleCheckerTest(BaseTest):
    def setUp(self):
        self.cryptoSetUp()

        self.old_trade = Trade.objects.create(
            crypto=self.crypto,
            type_of_trade=self.ruleset.type_of_ruleset,
            rule_set=self.ruleset,
            price=Decimal('250.0'),
            date=(timezone.now() - timezone.timedelta(hours=1)),
        )
        self.mp = MarketWatcherParser(self.mh, LOGGER)
        self.sp = SocialWatcherParser(self.sh, LOGGER)
        self.rc = RuleChecker(self.mp, self.sp, self.crypto, self.ruleset)

    def create_rule(self, type_of_rule, value):
        return Rule.objects.create(
            rule_set=self.ruleset,
            type_of_rule=type_of_rule,
            value=value
        )

    def create_test_type_of_rule(self, type_of_rule, val_when_true, val_when_false):
        rule = self.create_rule(type_of_rule, val_when_true)
        self.assertTrue(self.rc.run())
        rule.delete()
        rule = self.create_rule(type_of_rule, val_when_false)
        self.assertFalse(self.rc.run())
        rule.delete()

    def test_change_above(self):
        self.create_test_type_of_rule(Rule.CHANGE_ABOVE, 249.0, 250.0)

    def test_change_below(self):
        self.create_test_type_of_rule(Rule.CHANGE_BELOW, 251.0, 250.0)

    def test_perc_change_above(self):
        self.create_test_type_of_rule(Rule.CHANGE_PERC_ABOVE, 99.0, 100.0)

    def test_perc_change_below(self):
        self.create_test_type_of_rule(Rule.CHANGE_PERC_BELOW, 101.0, 100.0)

    def test_after_minutes(self):
        self.create_test_type_of_rule(Rule.AFTER_MINUTES, 50.0, 61.0)
