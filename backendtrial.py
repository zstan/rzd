import cgi, datetime, os, sys, webapp2

import urllib2, cookielib

import storage
import logging

from web import formResults
from mail import sendMail

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import background_thread

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('''
<ul>
  <li><h1>Backend Trial</h1></li>	
  <li><a href="#env">Environment Variables</a></li>
  <li><a href="#filesystem">File System</a></li>
  <li><a href="#request">Request Data</a></li>
</ul>

<hr noshade><h2 id="env">Environment Variables</h2><table>
''')
        keys = os.environ.keys()
        keys.sort()
        for k in keys:
            self.response.write('<tr><td valign="top"><code>%s</code></td>'
                                '<td valign="top"><code>%s</code></td></tr>'
                                % (cgi.escape(k),
                                   cgi.escape(str(os.environ[k]))))
        self.response.write('''
</table>

<hr noshade><h2 id="filesystem">File System</h2>
<pre>''')

        for path, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                self.response.write(
                    cgi.escape(os.path.join(path, filename)) + '\n')
        self.response.write('''
</pre>

<hr noshade><h2 id="request">Request Data</h2>
<pre>''')
        self.response.write(cgi.escape(sys.stdin.read()))
        self.response.write('</pre>')

        self.response.write('<hr noshade><p>The time is: %s</p>'
                            % str(datetime.datetime.now()))


def sendMailSummary():
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  reqs = storage.getMailPlan()
  if len(reqs):
    for item in reqs:
      logging.info('send train: ' + item.reqProps[5])
      results = formResults(item.reqProps, opener, item)
      if results:
        sendMail(item.account, results)
  else:
    logging.info('recipients list empty')

                          	
class SummaryMailPage(webapp2.RequestHandler):

  #cj = cookielib.CookieJar()
  #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  def post(self):
    tid = background_thread.start_new_background_thread(sendMailSummary, [])
    #t = background_thread.BackgroundThread(target=sendMailSummary, args=[])
    #t.start()
    #self.response.write('jopa')
    #sendMailSummary()

app = webapp2.WSGIApplication([
    #('/_ah/start', MainPage),
    (r'/backend/summary_mail', SummaryMailPage),
], debug=True)
