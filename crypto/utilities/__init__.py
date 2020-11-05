from datetime import timedelta

from django.utils import timezone
from django.db.models import F

from crypto.models import MarketHistoric, SocialHistoric

from .mailing import *
from .rule_checker import *


def get_mh_from_past(crypto, timedelta_=None):
    if timedelta_ is None:
        timedelta_ = timedelta(minutes=5)

    past_time = timezone.now() - timedelta_

    return MarketHistoric.objects.filter(
        crypto=crypto, date__gte=past_time, date__lte=past_time + timedelta(minutes=5),
    ).first()


def get_sh_from_past(crypto, timedelta_=None):
    if timedelta_ is None:
        timedelta_ = timedelta(minutes=5)

    past_time = timezone.now() - timedelta_

    return SocialHistoric.objects.filter(
        crypto=crypto, date__gte=past_time, date__lte=past_time + timedelta(minutes=5),
    ).first()


def get_mh_change(crypto, **timedelta_kwargs):
    latest_mh = get_mh_from_past(crypto)
    old_mh = get_mh_from_past(crypto, timedelta(**timedelta_kwargs))

    if latest_mh and old_mh:
        latest_price = float(latest_mh.price) or 1.0
        old_price = float(old_mh.price) or 1.0
        return ((latest_price - old_price) / old_price) * 100

    return 0.0


def get_data_for_crypto(crypto, timedelta_=None):
    """Get price from 7 days (timedelta) to now, in chart format."""
    if timedelta_ is None:
        timedelta_ = timedelta(days=7)

    past_time = timezone.now() - timedelta_
    data = (
        MarketHistoric.objects.filter(crypto=crypto, date__gte=past_time)
        .annotate(id_mod=F("id") % 100)
        .filter(id_mod=1)
        .order_by("date")
        .values_list("price", flat=True)
    )

    if data:
        first_value = data[0]
        data = [int(value - first_value) for value in data]
    return data
