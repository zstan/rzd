#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.api import users

import datetime

class User(ndb.Model):
  email     = ndb.StringProperty()
  confirmed = ndb.BooleanProperty()
  reqCount  = ndb.IntegerProperty()
  account   = ndb.UserProperty(required=True)
  reqProps  = ndb.StringProperty()
  reservedS = ndb.StringProperty()
  reservedI = ndb.IntegerProperty()
  date      = ndb.DateTimeProperty(auto_now_add=True)

class Req(ndb.Model):
  reqProps  = ndb.StringProperty()
  date      = ndb.DateTimeProperty(auto_now_add=True)

def addUser(mail):
  #clearStorage() # !!!!
  q = User.query()
  q = q.filter(User.email == mail)
  r = q.fetch(1)
  if not len(r):
    u = User(email = mail, 
             account=users.get_current_user(),
             date = datetime.datetime.now())
    u.put()

def getUsers():
  q = User.query().fetch()
  sOut = ''
  for result in q:
    sOut += result.email
  return sOut

def addReq(req):
  q = Req.query()
  q = q.filter(Req.reqProps == req)
  r = q.fetch(1)
  if not len(r):
    u = Req(reqProps = req,
        date = datetime.datetime.now())
    u.put()

def getReq():
  #clearStorage()
  q = Req.query().fetch()
  sOut = ''
  for result in q:
    sOut += result.reqProps + "  " +str(result.date) + '<br>'
  return sOut

def clearStorage():
  ndb.delete_multi(Req.query().fetch(keys_only=True))