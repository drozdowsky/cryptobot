import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from crypto.config import SMTP_SERVER, PORT, LOGIN, PASSWORD


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
    def __init__():
        pass
