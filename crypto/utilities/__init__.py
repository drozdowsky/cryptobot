from datetime import timedelta

from django.utils import timezone

from crypto.models import MarketHistoric, SocialHistoric

from .mailing import *
from .rule_checker import *


def get_mh_from_past(crypto, _timedelta=timedelta(minutes=5)):
    _datetime = timezone.now() - _timedelta

    mh = MarketHistoric.objects.filter(crypto=crypto,
                                       date__gte=_datetime,
                                       date__lte=_datetime + timedelta(minutes=5)
                                      ).first()
    return mh


def get_sh_from_past(crypto, _timedelta=timedelta(minutes=5)):
    _datetime = timezone.now() - _timedelta

    sh = SocialHistoric.objects.filter(crypto=crypto,
                                       date__gte=_datetime,
                                       date__lte=_datetime + timedelta(minutes=5)
                                      ).first()
    return sh


def get_mh_change(crypto, **timedelta_kwargs):
    _now = get_mh_from_past(crypto)
    _back_then = get_mh_from_past(crypto, timedelta(**timedelta_kwargs))

    if _now and _back_then:
        _now = float(_now.price) or 1.0
        _back_then = float(_now.pricce) or 1.0
        return ((_now - _back_then) / _back_then) * 100

    return 0.0
