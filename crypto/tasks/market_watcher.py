from decimal import Decimal

from crypto.market.api import BitBay
from crypto.models import get_or_create_crypto_model, MarketHistoric


def run_market_watcher_task(logger):
    # FIXME: crypto_hardcoded
    # FIXME: currency_hardocded
    try:
        crypto_model = get_or_create_crypto_model('Ethereum', 'ETH')
        bb = BitBay('ETH', 'PLN')
        bid_val, ask_val = bb.bids_value, bb.asks_value
        transaction_value = bb.transaction_value/50
        last = Decimal(bb.last)

        mh = MarketHistoric(crypto=crypto_model, price=last,
                            bids_value=bid_val, asks_value=ask_val,
                            avg_transaction_value=transaction_value,
                            response_json=bb.json)
        # datetime = auto_now_add = True
        mh.save()
    except Exception as ex:
        logger.error('[MWT] {ex}.'.format(ex=str(ex)))
        return None

    return mh
