
from google.appengine.api import mail

def sendMail(body):
  mail.send_mail(sender="rzd.ru Support <@gmail.com>",
                to="@mail.ru <@mail.ru>",
                subject="train report",
                body=body)