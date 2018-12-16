from django.db import models
from django.conf import settings


class CryptoModel(models.Model):
    short_name = models.CharField(max_length=11, unique=True)
    long_name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return '{} [{}]'.format(self.long_name, self.short_name)


def get_or_create_crypto_model(long_name, short_name):
    crypto, _ = CryptoModel.objects.get_or_create(long_name=long_name.capitalize(), short_name=short_name.upper())
    return crypto


class MarketHistoric(models.Model):
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} at {}'.format(self.crypto.long_name, self.value, self.date)

    def __sub__(self, other):
        return abs(self.value - other.value)

    class Meta:
        ordering = ('date',)
        get_latest_by = "date"


class SocialHistoric(models.Model):
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {} at {}'.format(self.crypto.long_name, self.value, self.date)

    def __sub__(self, other):
        return abs(self.value - other.value)

    class Meta:
        ordering = ('date',)
        get_latest_by = "date"


class RuleSet(models.Model):
    name = models.CharField(max_length=32)
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.name)


class Rule(models.Model):
    RULE_TYPES = [
        'buy_below',
        'sell_above',
        'buy_max_value_perc',
        'sell_max_value_perc',
        'buy_max_value',
        'sell_max_value',
        'after_hours',
    ]

    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)
    rule_set = models.ForeignKey(RuleSet, null=False, on_delete=models.CASCADE, related_name='rules')
    value = models.IntegerField(null=True)
    type_of_rule = models.IntegerField(null=False)  # we use this integer as a index for RULE_TYPES


class Trade(models.Model):
    date = models.DateTimeField(auto_now=True)
    type_of_trade = models.CharField(max_length=11)
    amount = models.DecimalField(default=0.0, decimal_places=8, max_digits=12)
    price = models.DecimalField(default=0.0, decimal_places=2, max_digits=12)
    rule_set = models.ForeignKey(RuleSet, related_name='trades', null=True, on_delete=models.SET_NULL)
    crypto = models.ForeignKey(CryptoModel, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return '{typeof}: {amount}{crypto} for {price}'.format(typeof=self.type_of_trade, amount=self.amount,
                                                               crypto=self.crypto.short_name, price=self.price)

    class Meta:
        ordering = ('-date',)
        get_latest_by = "date"
