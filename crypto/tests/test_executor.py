from unittest.mock import patch

from crypto.tests import *
from crypto.tasks.executor import Executor
from crypto.tasks.market_watcher import MarketWatcherParser
from crypto.tasks.social_watcher import SocialWatcherParser


class RuleCheckerTest(BaseTest):
    def setUp(self):
        self.cryptoSetUp()

        self.old_trade = Trade.objects.create(
            type_of_trade=self.ruleset.type_of_ruleset,
            rule_set=self.ruleset,
            price=Decimal("250.0"),
            date=(timezone.now() - timezone.timedelta(hours=1)),
        )

        self.mp = MarketWatcherParser(self.mh, LOGGER)
        self.sp = SocialWatcherParser(self.sh, LOGGER)
        self.executor = Executor(self.mp, self.sp, self.crypto, LOGGER)

    @patch("crypto.tasks.executor.MailGenerator.run", return_value=0)
    def test_only_rule_above(self, mock_generator):
        initial_trades = Trade.objects.count()
        Rule.objects.create(rule_set=self.ruleset, type_of_rule=Rule.ABOVE, value=251)
        self.executor.run()
        mock_generator.assert_called_once()
        assert Trade.objects.count() == initial_trades + 1

    @patch("crypto.tasks.executor.MailGenerator.run", return_value=0)
    def test_only_rule_below(self, mock_generator):
        initial_trades = Trade.objects.count()
        Rule.objects.create(rule_set=self.ruleset, type_of_rule=Rule.BELOW, value=501)
        self.executor.run()
        mock_generator.assert_called_once()
        assert Trade.objects.count() == initial_trades + 1

    @patch("crypto.tasks.executor.MailGenerator.run", return_value=0)
    def test_only_rule_change_perc_above(self, mock_generator):
        initial_trades = Trade.objects.count()
        Rule.objects.create(
            rule_set=self.ruleset, type_of_rule=Rule.CHANGE_PERC_ABOVE, value=99
        )
        self.executor.run()
        mock_generator.assert_called_once()
        assert Trade.objects.count() == initial_trades + 1

    @patch("crypto.tasks.executor.MailGenerator.run", return_value=0)
    def test_only_rule_limit(self, mock_generator):
        initial_trades = Trade.objects.count()
        Rule.objects.create(
            rule_set=self.ruleset, type_of_rule=Rule.EXEC_LIMIT, value=1
        )
        self.executor.run()
        mock_generator.assert_not_called()
        assert Trade.objects.count() == initial_trades  # limit!

    @patch("crypto.tasks.executor.MailGenerator.run", return_value=0)
    def test_only_rule_two_rules(self, mock_generator):
        initial_trades = Trade.objects.count()
        Rule.objects.create(
            rule_set=self.ruleset, type_of_rule=Rule.EXEC_LIMIT, value=2
        )
        Rule.objects.create(
            rule_set=self.ruleset, type_of_rule=Rule.CHANGE_PERC_ABOVE, value=99
        )
        self.executor.run()
        assert Trade.objects.count() == initial_trades + 1
