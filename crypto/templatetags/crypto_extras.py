from django.template import Library

register = Library()


@register.filter
def hash(h, key):
    return h.get(key)


@register.filter
def reverse_trade(h):
    if h == 'E':
        return 'Email'
    elif h == 'B':
        return 'Buy'
    elif h == 'S':
        return 'Sell'

    return ''
