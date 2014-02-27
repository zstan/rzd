#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.api import users
import logging

import time
from datetime import datetime
from myhashlib import getHashForUser

class User(ndb.Model):
  email     = ndb.StringProperty()
  confirmed = ndb.BooleanProperty()
  reqCount  = ndb.IntegerProperty(default=1)
  account   = ndb.UserProperty(required=True)
  reqProps  = ndb.StringProperty(repeated=True)
  date      = ndb.DateTimeProperty(auto_now_add=True)
  premium   = ndb.BooleanProperty()
  active    = ndb.BooleanProperty()
  accHash   = ndb.StringProperty()
  reservedS = ndb.StringProperty()
  reservedI = ndb.IntegerProperty()

class Req(ndb.Model):
  reqProps  = ndb.StringProperty()
  date      = ndb.DateTimeProperty(auto_now_add=True)

def addUserTrainReq(reqProps):
  user = users.get_current_user()
  if user:

    items = reqProps.split('|')
    ditems = items[4].split('.')
    d1 = datetime(year=int(ditems[2]), month=int(ditems[1]), day=int(ditems[0]), hour=int(ditems[3]))

    q = User.query()
    logging.info('fetch user: ' + user.email())
    q = q.filter(User.account == user)
    r = q.fetch(1)
    if not len(r):
      u = User(account=user,
               date = d1,
               reqProps = items, active = True, accHash = getHashForUser(user))
      u.put()
      return 'request registred'

    else:
      logging.info('update already exist user: ' + user.email())
      currentUserInfo = r[0]
      if not currentUserInfo.active:              
        currentUserInfo.active = True
        currentUserInfo.reqCount = currentUserInfo.reqCount + 1
        currentUserInfo.date = d1
        currentUserInfo.reqProps = items
        currentUserInfo.put()
        return 'request registred'
      else:
        logging.info('can\'t update already have active req: ' + user.email())
        return 'can\'t register request, already have active request'

def getMailPlan():
  d0 = datetime.fromtimestamp(time.time() + 14400)
  q = User.query().filter(User.active == True)
  sendList = []
  for result in q:
    if (result.date < d0):
      result.active = False
      logging.info('disable user activity by time: ' + result.account.email())
      result.put()
    else:
      sendList.append(result)
  return sendList

def disableTrainReq(h):
  logging.info('disable hash: %s' % h)
  q = User.query().filter(User.accHash == h)
  r = q.fetch(1)
  if len(r):
    logging.info('found hash')
    currentUserInfo = r[0]
    currentUserInfo.active = False
    currentUserInfo.put()
    return 'request disabled'

def getUsers():
  #clearStorage() # !!!!
  q = User.query().fetch()
  sOut = ''
  for result in q:
    sOut += "%s active=%s reqCount=%d hash=%s" % (result.account.email(), str(result.active), result.reqCount, result.accHash)
  return sOut

def addReq(req):
  q = Req.query()
  req = req.lower()
  q = q.filter(Req.reqProps == req)
  r = q.fetch(1)
  if not len(r):
    u = Req(reqProps = req,
            date = datetime.fromtimestamp(time.time() + 14400))
    u.put()

def getReq():
  #clearStorage()
  q = Req.query().fetch()
  sOut = ''
  for result in q:
    sOut += "%s %s\n" % (result.reqProps, str(result.date))
  return sOut

def clearStorage():
  ndb.delete_multi(User.query().fetch(keys_only=True))