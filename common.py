#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from google.appengine.api import users

import urllib2, httplib, json
from time import sleep

def getResponse(url, opener = None):
  good = False
  while not good:
    try:
      resp = None
      if not opener:
        resp = urllib2.urlopen(url, timeout=60)
      else:
        resp = opener.open(url, timeout=60)
      if resp.getcode() in [httplib.OK, httplib.CREATED, httplib.ACCEPTED]:
        good = True
    except (urllib2.HTTPError, httplib.HTTPException):
      pass
  return resp.read()

def getResponseStub(url, opener):
  r = json.loads(getResponse(url, opener))
  cnt = 0
  while (r['result'].lower()!='ok' and cnt < 5):
    sleep(1)
    cnt+=1
    r = json.loads(getResponse(url, opener))
  return r

def getCurrentGoogleUserCode():
  user = users.get_current_user()
  if not user:      
    return '<br>'*18+'<font color="red">Log in, with google account, no new registration needed!</font><a href="%s">&nbsp;log in</a><br>' % users.create_login_url()
  else:
    return '<br>'*18+'<font color="red">Hello, %s, %s!</font><a href="%s">&nbsp;log out</a>' % (user.nickname(), user.email(), users.create_logout_url('/'))

