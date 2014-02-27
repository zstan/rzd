
from google.appengine.api import mail

def sendMail(account, body):
  mail.send_mail(sender  = "rzd wrapper support <robot.rzd@gmail.com>",
                 to      = account.email(),
                 subject = "train report",
                 html    = body,
                 body    = body)