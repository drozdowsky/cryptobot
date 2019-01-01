from . import config
from .mail import send_email
from .currency import DowntimeException

from .models import get_or_create_crypto_model
from .market.api import BitBay
from .currency import Currency
from .middleman.middleman import Middleman
from .bot import BotBase


def run(logger):
    logger.info('I am running!')
    eth_pln = BitBay('ETH', 'PLN')
    # btc_pln = BitBay('BTC', 'PLN')

    ether_model = get_or_create_crypto_model('Ethereum', 'ETH')

    currencies = [
        Currency(ether_model, 'PLN', 8, eth_pln, 180),
        # Currency(CryptoModel.objects.get_or_create(short_name='BTC', long_name='Bitcoin'), 'PLN', 8, btc_pln, 360),
    ]

    middlemen = [
        Middleman(None, eth_pln, BotBase('EtherBot', ether_model), ether_model)
    ]

    title = []
    body = []

    try:
        for index, currency in enumerate(currencies):
            temp_title, temp_body = currency.generate_mail_lists()
            title.extend(temp_title)
            body.extend(temp_body)

            try:
                for item, value in middlemen[index].process_crypto().items():
                    body.append('{}: {}<br/>\n'.format(item, value))
            except IndexError:
                pass

            body.append('<br/>\n')

            logger.info('{}: {} {:.2f}%. From {} ({}) to {}'.format(currency.crypto.short_name,
                                                                    currency.value,
                                                                    currency.percent,
                                                                    currency.cached.last_update.replace(microsecond=0),
                                                                    currency.cached.value,
                                                                    currency.last_update.replace(microsecond=0),
                                                                    ))

        if len(title) > 0:
            send_email(config.SMTP_SERVER, config.PORT, config.LOGIN, config.PASSWORD, config.RECIPENTS,
                       ' '.join(title),
                       '<br/>\n'.join(body)
                       )
            logger.info('Email sent!')

        return True

    except DowntimeException:
        if logger is not None:
            logger.warning('Warning:: DowntimeException')

    except Exception as e:
        if logger is not None:
            logger.warning('Warning:: On run: ' + str(e))

    return False
