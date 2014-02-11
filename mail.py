
from google.appengine.api import mail

def sendMail(body):
  mail.send_mail(sender="Example.com Support <@gmail.com>",
                to="Albert Johnson <@mail.ru>",
                subject="simple body",
                body=body)