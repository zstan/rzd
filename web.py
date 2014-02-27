#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import cgi, os

from google.appengine.api import users
from google.appengine.runtime import DeadlineExceededError

from time import sleep
from datetime import datetime

from startpage import getMainPage
from mail import sendMail
from common import getResponse, getResponseStub, getCurrentGoogleUserCode

import storage

import webapp2
import urllib, urllib2, cookielib, json, urlparse
import logging, time


suggestDict = {}
suggestDictSize = 5000

redFont0 = '<font size=\"2\" color=\"red\">'
grayFont0 = '<font size=\"2\" color=\"#B3B3B3\">' 
fontClose = '</font>'
NoSeats = '<br>&nbsp;%s%s%s<br>' % (grayFont0, u'все билеты раскупили, негодяи:(', fontClose)
domainPrefix = 'rzdzstan0'

def getCityId(city, s):
  req = 'http://pass.rzd.ru/suggester?lang=ru&stationNamePart=%s' % urllib.quote(city.encode('utf-8'))
  respData = getResponse(req)
  rJson = json.loads(respData)
  for item in rJson:
    if item['name'].lower() == city.lower():
      s.response.out.write(u'Найден: %s : %s<br>' % (item['name'], item['id']))
      return item['id']
  s.response.out.write(u'Не найден: %s<br>' % city)
  s.response.out.write(u'Выбранный вами город не найден, попробуйте еще раз:&nbsp;&nbsp;<a href="../">Вернуться</a><br>')
  return None

def formResults(reqList, opener, item = None):

  if item:
    trainNum4mail = item.reqProps[5]

  st0  = urllib.quote(reqList[0].encode('utf-8'))
  st1  = urllib.quote(reqList[2].encode('utf-8'))
  id0  = reqList[1]
  id1  = reqList[3]
  date = reqList[4]

  if (not id0 or not id1):
    return

  req1 = 'http://pass.rzd.ru/timetable/public/ru?STRUCTURE_ID=735&layer_id=5371&dir=0&tfl=3&checkSeats=0&withoutSeats=y&st0=%s&code0=%s&dt0=%s&st1=%s&code1=%s&dt1=%s' % (st0, id0, date, st1, id1, date)

  out = '<html><body><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'

  r = json.loads(getResponse(req1, opener))
  if (r['result'].lower()=='ok'):
    try:
      out += r['tp'][0]['msgList'][0]['message'] + '<br>'
    except IndexError, e:
      logging.error('msgList Error: ' + str(r))
    return out
  try:
    sid = str(r['SESSION_ID'])
    rid = str(r['rid'])
  except KeyError, e:
    logging.error('Error: ' + str(r))
    return str(e)

  req2 = req1+'&rid=%s&SESSION_ID=%s' % (rid, sid)

  r = getResponseStub(req2, opener)
  
  out += '<form name="FinalAccept" method="get" action="sendme"><br>'
  if ('tp' in r):
    r = r['tp'][0]
    out += '<br>' + redFont0 + r['from'] + ' -> '
    out += r['where'] + fontClose + '<br>'
    out += r['date'] + '<br>'
    l_trains = r['list']
    for train in l_trains:

      trainNum = train['number']
      if item and trainNum4mail!=trainNum:
        continue

      out += '<hr color="red" size="3" width="50%" align="left"/><br>'

      disableReport = 'disabled'
      user = users.get_current_user()
      #if user and user.email() in ['test@example.com']:
      if user:
        disableReport = ''

      if not item:
        data2mail = ('%s|%s|%s|%s|%s|%s') % (reqList[0], reqList[1], reqList[2], reqList[3], date + '.' + train['time0'].split(':')[0], trainNum)
        out += u'<input type="radio" name="trainReq" %s onclick="this.form.submit();" value="%s">заказать отчет на почту<br><br>' % (disableReport, data2mail)
      out += u'&nbsp;станция отправления: %s <br>' % train['station0']
      out += u'&nbsp;станция прибытия: ' + train['station1'] + '<br>'
      out += u'&nbsp;время в пути: ' + train['timeInWay'] + '<br>'
      out += u'&nbsp;время отправления: ' + train['time0'] + '<br>'
      out += u'&nbsp;время прибытия: ' + train['time1'] + '<br>'
      bFirm = ''
      if 'bFirm' in train:
        bFirm = redFont0 + u' (фирменный)' + fontClose
      out += u'&nbsp;номер поезда: %s %s<br>' % (trainNum, bFirm)
      if len(train['cars'])==0:        
        out += NoSeats
      else:
        for car in train['cars']:
          out += '<hr color="gray" size="1" width="30%" align="left"/>'
          out += u'&nbsp;тип: %s<br>' % car['typeLoc']
          freeSeats = car['freeSeats']
          if int(freeSeats) <= 10:
            freeSeats = '%s%s%s' % (redFont0, freeSeats, fontClose)
          out += u'&nbsp;свободных мест: %s <br>' % freeSeats
          out += u'&nbsp;цена: %s руб. <br>' % car['tariff']
    if item:
      out += u'<br><a href="http://www.%s.appspot.com/sendme?reject=%s">Отписаться</a>' % (domainPrefix, item.accHash)

  else:
    out += "Some error occured: " + str(r)
  #out += '</form></body></html>'
  out += '</form></body></html>'

  return out

def getRidSid(st0, st1, date, s):
  """
  username = 'user'
  password = 'pass'
  login_data = urllib.urlencode({'j_username' : username, 'j_password' : password, 'action' : 'Вход'})

  good = False
  while not good:
    try:
      opener.open('https://pass.rzd.ru/ticket/j_security_check', login_data)
      good = True
    except urllib2.HTTPError, e:
      s.response.out.write('fail')
      cj.clear_session_cookies() 
  """

  id0 = getCityId(st0, s)
  id1 = getCityId(st1, s)

  out = formResults((st0, id0, st1, id1, date), s.opener)
  s.response.out.write(out)
  

class MainPage(webapp2.RequestHandler):
  
  def get(self):
    mainPage = getMainPage() % getCurrentGoogleUserCode()
    self.response.out.write(mainPage)

def getProperDate(date):
  items = date.split('/')
  sOut = ''
  try:
    sOut = ('%s.%s.%s' % (items[1], items[0], items[2]))
  except (IndexError):
    logging.error('IndexError: ' + date)
    sOut = time.strftime('%d.%m.%Y', time.gmtime(time.time() + 14400)) # mega fake, wan`t use pytz
  return sOut

class TrainListPage(webapp2.RequestHandler):
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  def post(self):
      self.response.out.write('<html><body>Результаты поиска:<pre>')
      st0  = cgi.escape(self.request.get('from'))
      st1  = cgi.escape(self.request.get('to'))
      storage.addReq('%s -> %s' % (st0, st1))
      date = getProperDate(cgi.escape(self.request.get('date')))
      
      try:
        getRidSid(st0, st1, date, self)
      except DeadlineExceededError:
        self.response.clear()
        self.response.set_status(500)
        self.response.out.write("This operation could not be completed in time... st0 %s st1 %s date %s" % (st0, st1, date))
      self.response.out.write('</pre></body></html>')

class SuggesterPage(webapp2.RequestHandler):

    def get(self):
        global suggestDict
        suggOut = '[]'

        try:
          station = self.request.get('stationNamePart')
          stationKey = station[:3]

          sStations = set()

          if stationKey in suggestDict:
            sStations = suggestDict[stationKey]
          else:
            req = 'http://pass.rzd.ru/suggester?lang=ru&stationNamePart=%s' % urllib.quote(station.encode('utf-8'))
            respData = getResponse(req)

            if len(respData) > 0:
              rJson = json.loads(respData)
              for item in rJson:
                sStations.add(item['name'])

          suggOut = '['              
          lStations = self.sort4Find(sStations, station.lower())[:15]
          cnt = 1
          for item in lStations:
            suggOut += '{"id":"%d","label":"%s","value":"%s"},' % (cnt, item, item)
            cnt += 1
          suggOut = suggOut[:-1]
          suggOut += ']'

          if len(suggestDict) < suggestDictSize: #one more stub !!!
            suggestDict[stationKey] = sStations

          self.response.out.write(suggOut)

        except (TypeError, ValueError):
          self.response.out.write(suggOut)

    def sort4Find(self, sStations, suggest):
      l0 = []
      l1 = []
      for station in sStations:
        if station.lower().find(suggest) == 0:
          l0.append(station)
        else:
          l1.append(station)
      return l0 + l1

class SendMePage(webapp2.RequestHandler):

  def get(self):
    trainReq    = self.request.get('trainReq')
    trainReject = self.request.get('reject')
    if (trainReq):
      logging.info('trainReq')
      ret = storage.addUserTrainReq(self.request.get('trainReq'))
      self.response.out.write(str(ret))
    elif (trainReject):
      logging.info('trainReject')
      storage.disableTrainReq(trainReject)

class SummaryMailPage(webapp2.RequestHandler):

  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  def get(self):
    reqs = storage.getMailPlan()
    if len(reqs):
      for item in reqs:
        logging.info('send train: ' + item.reqProps[5])
        results = formResults(item.reqProps, self.opener, item)
        sendMail(item.account, results)
    else:
      logging.info('recipients list empty')

class StatPage(webapp2.RequestHandler):

  def get(self):
    #resp = opener.open('http://pass.rzd.ru/suggester?lang=ru&stationNamePart=%D0%B9%D0%B9%D0%B9')
    #self.response.out.write(resp.read())
    self.response.out.write(storage.getUsers())
    self.response.out.write('\n\n')
    self.response.out.write(storage.getReq()+'\n')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/trains', TrainListPage),
    ('/suggester', SuggesterPage),
    ('/sendme', SendMePage),
    ('/summary_mail', SummaryMailPage),
    ('/stat', StatPage)
], debug=False)
