
from google.appengine.api import mail

def sendMail(toAddr, body):
  mail.send_mail(sender="rzd wrapper support <robot.rzd@gmail.com>",
                to=toAddr,
                subject="train report",
                html=body,
                body=body)