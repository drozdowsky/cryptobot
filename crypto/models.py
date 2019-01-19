from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings


class CryptoModel(models.Model):
    short_name = models.CharField(max_length=11, unique=True)
    long_name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return '{} [{}]'.format(self.long_name, self.short_name)


def get_or_create_crypto_model(long_name, short_name):
    crypto, _ = CryptoModel.objects.get_or_create(
        long_name=long_name.capitalize(),
        short_name=short_name.upper()
    )
    return crypto


class MarketHistoric(models.Model):
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    bids_value = models.FloatField()
    asks_value = models.FloatField()
    avg_transaction_value = models.FloatField()
    price = models.DecimalField(default=1.0, decimal_places=2, max_digits=19)
    response_json = JSONField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} at {}'.format(self.crypto.long_name, self.price,
                                     self.date)

    def __sub__(self, other):
        return abs(self.price - other.price)

    class Meta:
        ordering = ('date',)
        get_latest_by = "date"


class SocialHistoric(models.Model):
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    gtrends_top_7d = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} at {}'.format(self.crypto.long_name, self.gtrends_top_7d,
                                     self.date)

    class Meta:
        ordering = ('date',)
        get_latest_by = "date"


class CryptoWallet(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crypto = models.ForeignKey(CryptoModel, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.0, decimal_places=8, max_digits=19)

    class Meta:
        # django does not have composite primary keys - workaround here
        unique_together = ('owner', 'crypto')


class CurrencyWallet(models.Model):
    # we store this as table because this gives room for future improvements
    # (mulitple wallets etc.)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True,
                                 on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.0, decimal_places=2, max_digits=19)


class RuleSet(models.Model):
    EMAIL_ONLY = 'E'
    BUY = 'B'
    SELL = 'S'

    RULESET_TYPES = [
        (EMAIL_ONLY, 'email_only'),
        (BUY, 'buy'),
        (SELL, 'sell')
    ]

    name = models.CharField(max_length=128)
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE,
                               related_name="rulesets")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False,
                              on_delete=models.CASCADE)
    type_of_ruleset = models.CharField(max_length=1, choices=RULESET_TYPES,
                                       default=EMAIL_ONLY)

    def __str__(self):
        return '{}'.format(self.name)


class Rule(models.Model):
    BELOW = 'BEL'
    ABOVE = 'ABO'
    CHANGE_ABOVE = 'CGA'
    CHANGE_BELOW = 'CGB'
    CHANGE_PERC_ABOVE = 'CPA'
    CHANGE_PERC_BELOW = 'CPB'
    MAX_VALUE_PERC = 'MVP'
    MAX_VALUE = 'MVE'
    AFTER_MINUTES = 'AHS'
    MBOT_ABOVE = 'MBA'
    MBOT_BELOW = 'MBB'
    SBOT_ABOVE = 'SBA'
    SBOT_BELOW = 'SBB'

    RULE_TYPES_FULL = [
        (BELOW, 'below', 'Price is below (PLN)'),
        (ABOVE, 'above', 'Price is above (PLN)'),
        (CHANGE_ABOVE, 'change_above', 'Price change is above (PLN)'),
        (CHANGE_BELOW, 'change_below', 'Price change is below (PLN)'),
        (CHANGE_PERC_ABOVE, 'change_perc_above', 'Price percent change is above (%)'),
        (CHANGE_PERC_BELOW, 'change_perc_below', 'Price percent change is below (%)'),
        # (MAX_VALUE_PERC, 'max_value_perc'),
        # (MAX_VALUE, 'max_value'),
        (AFTER_MINUTES, 'after_minutes', 'Wait at least (minutes)'),
        (MBOT_ABOVE, 'market_bot_above', 'Market Bot is above (0.0-2.0)'),
        (MBOT_BELOW, 'market_bot_below', 'Market Bot is below (0.0-2.0)'),
        (SBOT_ABOVE, 'social_bot_above', 'Social Bot is above (0.0-2.0)'),
        (SBOT_BELOW, 'social_bot_below', 'Social Bot is below (0.0-2.0)'),
    ]

    RULE_TYPES = [
        (sc, full_name) for sc, full_name, _ in RULE_TYPES_FULL
    ]
    RULE_TYPES_DICT = {sc: full_name for sc, full_name in RULE_TYPES}
    RULE_DESC = [(sc, desc) for sc, _, desc in RULE_TYPES_FULL]

    #  unique_together = ('rule_set', 'value', 'type_of_rule')
    rule_set = models.ForeignKey(RuleSet, null=False, on_delete=models.CASCADE,
                                 related_name='rules')
    value = models.FloatField(null=False)
    type_of_rule = models.CharField(max_length=3, choices=RULE_TYPES)

    class Meta:
        unique_together = ('rule_set', 'value', 'type_of_rule')


class Trade(models.Model):
    TRADE_TYPES = RuleSet.RULESET_TYPES

    date = models.DateTimeField(auto_now=True)
    type_of_trade = models.CharField(max_length=1, choices=TRADE_TYPES)
    amount = models.DecimalField(default=0.0, decimal_places=8, max_digits=19)
    price = models.DecimalField(default=1.0, decimal_places=2, max_digits=19)
    rule_set = models.ForeignKey(RuleSet, related_name='trades', null=True,
                                 on_delete=models.SET_NULL)
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{typeof}: {amnt}{crypto} for {price}'.format(typeof=self.type_of_trade,
                                                             amnt=self.amount,
                                                             crypto=self.crypto.short_name,
                                                             price=self.price)

    class Meta:
        ordering = ('-date',)
        get_latest_by = "date"
