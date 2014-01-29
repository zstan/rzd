
from google.appengine.api import mail

def sendMail():
  mail.send_mail(sender="Example.com Support <@gmail.com>",
                to="Albert Johnson <@mail.ru>",
                subject="test mail",
                body="""
  Dear Albert:

  Your example.com account has been approved.  You can now visit
  http://www.example.com/ and sign in using your Google Account to
  access new features.

  Please let us know if you have any questions.

  The example.com Team
  """)