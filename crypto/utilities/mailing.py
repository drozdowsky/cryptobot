import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from crypto.config import LOGIN, PASSWORD, PORT, SMTP_SERVER

from django.utils import timezone
from datetime import timedelta

def get_now():
    return str(timezone.now().replace(microsecond=0))


def send_email(recipient, subject, body):
    mail_user = LOGIN
    mail_pwd = PASSWORD
    FROM = LOGIN
    TO = recipient if type(recipient) is list else [recipient]

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = FROM
    message['To'] = ", ".join(TO)

    message.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP_SSL(SMTP_SERVER, int(PORT))
    server.ehlo()

    server.login(mail_user, mail_pwd)

    server.sendmail(FROM, TO, message.as_string())
    server.quit()


class MailGenerator:
    def __init__(self, crypto, rs, mp, sp, executor_results, past_price, logger):
        self.crypto = crypto
        self.rs = rs
        self.mp = mp
        self.sp = sp
        self.results = executor_results
        self.logger = logger
        self.email = rs.owner.email
        self.past_price = past_price

    def run(self):
        if not self.email:
            return 3

        title, body = self.generate_mail()
        body = '<br>\n'.join(body)
        title = ' '.join(title)
        send_email(self.email, title, body)
        return 0

    def generate_mail(self):
        """
            BELOW = 'BEL'
            ABOVE = 'ABO'
            CHANGE_ABOVE = 'CGA'
            CHANGE_BELOW = 'CGB'
            CHANGE_PERC_ABOVE = 'CPA'
            CHANGE_PERC_BELOW = 'CPB'
            MAX_VALUE_PERC = 'MVP'
            MAX_VALUE = 'MVE'
            AFTER_HOURS = 'AHS'
            MBOT_ABOVE = 'MBA'
            MBOT_BELOW = 'MBB'
            SBOT_ABOVE = 'SBA'
            SBOT_BELOW = 'SBB'
        """
        yesterday_price = self.get_past_price()
        title_list = [
            '[{}]'.format(self.rs.type_of_ruleset),
            '{}'.format(self.crypto.long_name),
            yesterday_price,
        ]

        body_list = [
            '<b>{}</b>:'.format(str.upper(self.crypto.long_name)),

            # FIXME: hardcoded_currency
            '{0} price: {1}PLN {2}'.format(
                self.crypto.short_name, self.mp.mh.price, yesterday_price
            ),
        ]

        self.add_format_from_rule_checker(body_list)

        return title_list, body_list

    def add_format_from_rule_checker(self, body_list):
        after_hours_date = self.results.get('AHS')
        if after_hours_date:
            body_list.append('From {} to {}'.format(
                str(after_hours_date.replace(microsecond=0)),
                get_now()
            ))

        below, above = self.results.get('BEL'), self.results.get('ABO')
        if below or above:
            body_list.append('Price went from {}PLN to {}PLN'.format(
                below or above, self.mp.mh.price
            ))

        below_c, above_c = self.results.get('CGA'), self.results.get('CGB')
        if below_c or above_c:
            body_list.append('Price difference: {}PLN'.format(
                below_c or above_c
            ))

        below_c_p, above_c_p = self.results.get('CPA'), self.results.get('CPB')
        if below_c_p or above_c_p:
            body_list.append('Price difference: {} %'.format(
                below_c_p or above_c_p
            ))

        if self.rs.type_of_ruleset != 'E':
            mvp, mve = self.results.get('MVP'), self.results.get('MVE')
            _change_list = []
            if mve:
                # FIXME: hardcoded_crypto
                _change_list.append('[{}ETH]'.format(str(mve)))
            if mve:
                _change_list.append('[{}%]'.format(str(mvp)))

            if _change_list:
                body_list.append("Using {} of user's wallet".format(
                    ' '.join(_change_list))
                )

        # market bot _above, _below
        mb_a, mb_b = self.results.get('MBA'), self.results.get('MBB')
        if mb_a or mb_b:
            body_list.append('Market Bot: {}'.format(mb_a or mb_b))

        # social bot _above, _below
        sb_a, sb_b = self.results.get('SBA'), self.results.get('SBB')
        if sb_a or sb_b:
            body_list.append('Social Bot: {}'.format(sb_a or sb_b))

    def get_past_price(self):
        if not self.past_price:
            return ''

        past_price = float(self.past_price.price)
        now_price = float(self.mp.mh.price)

        if not past_price or not now_price:
            return ''

        date_range = (self.mp.mh.date - self.past_price.date)
        if timedelta(hours=23) < date_range < timedelta(hours=25):
            _perc = (float(now_price - past_price) / float(now_price)) * 100
            _format_string = '[24h/{3:+.2f} %]'.format(_perc)
            return _format_string

        return ''
