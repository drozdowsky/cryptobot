import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(smtp, port,
               user, pwd,
               recipient,       # can be list
               subject, body
               ):

    mail_user = user
    mail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]

    #SUBJECT = subject
    #TEXT = body

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = FROM
    message['To'] = ", ".join(TO)

    #message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    #""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

    message.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP_SSL(smtp, int(port))
    server.ehlo()

    server.login(mail_user, mail_pwd)

    server.sendmail(FROM, TO, message.as_string())
    server.quit()

