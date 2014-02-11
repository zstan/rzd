#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import cgi, os

from google.appengine.api import users
from time import sleep
from httplib import HTTPException, HTTPConnection
import webapp2, httplib
import urllib, urllib2, cookielib, json
from autocomplete import getMainPage
from mail import sendMail
from google.appengine.runtime import DeadlineExceededError
import logging, storage

mainPage = None # temporary stub !!!
suggestDict = {}
suggestDictSize = 5000

redFont0 = '<font size=\"2\" color=\"red\">'
redFont1 = '</font>'

def getResponse(url, opener = None):
  good = False
  while not good:
    try:
      resp = None
      if not opener:
        resp = urllib2.urlopen(url, timeout=5)
      else:
        resp = opener.open(url, timeout=5)
      if resp.getcode() in [httplib.OK, httplib.CREATED, httplib.ACCEPTED]:
        good = True
    except (urllib2.HTTPError, HTTPException):
      pass
  return resp.read()

def getResponseStub(url, opener):
  r = json.loads(getResponse(url, opener))
  cnt = 0
  while (r['result']!='OK' and cnt < 5):
    sleep(1)
    cnt+=1
    r = json.loads(getResponse(url, opener))
  return r

def getCityId(city, s):
  req = 'http://pass.rzd.ru/suggester?lang=ru&stationNamePart=' + urllib.quote(city.encode('utf-8'))
  respData = getResponse(req)
  rJson = json.loads(respData)
  for item in rJson:
    if item['name'].lower() == city.lower():
      s.response.out.write(u'Найден: '+item['name']+' -> '+str(item['id'])+'<br>')
      return str(item['id'])
  s.response.out.write(u'Не найден: '+city+'<br>')
  s.response.out.write(u'Выбранный вами город не найден, попробуйте найти в списке и ввести еще раз:<a href="../">Вернуться</a><br>')
  for item in rJson:
    s.response.out.write(item['name']+'<br>')
  return None

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

  st0 = urllib.quote(st0.encode('utf-8'))
  st1 = urllib.quote(st1.encode('utf-8'))

  if (not id0 or not id1):
    return
  
  req1 = 'http://pass.rzd.ru/timetable/public/ru?STRUCTURE_ID=735&layer_id=5371&dir=0&tfl=3&checkSeats=1&st0=%s&code0=%s&dt0=%s&st1=%s&code1=%s&dt1=%s' % (st0, id0, date, st1, id1, date)

  r = json.loads(getResponse(req1, s.opener))
  if (r['result'].lower()=='ok'):
    s.response.out.write(r['tp'][0]['msgList'][0]['message']) #errType
    s.response.out.write('<br>')
    #s.response.out.write(r)
    return
  sid = str(r['SESSION_ID'])
  rid = str(r['rid'])

  req2 = req1+'&rid='+rid+'&SESSION_ID='+sid

  r = getResponseStub(req2, s.opener)
  
  out = '<html><body><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
  if ('tp' in r):
    out += '<br>' + redFont0 + r['tp'][0]['from'] + ' -> '
    out += r['tp'][0]['where'] + redFont1 + '<br>'
    out += r['tp'][0]['date'] + '<br>'
    l_trains = r['tp'][0]['list']
    #print l_trains
    for train in l_trains:
      out += '<hr color="red" size="3" width="50%" align="left"/><br>'
      out += u'<input type="radio" name="radAnswer" id=%s/ disabled="true">заказать отчет на почту<br>' % req1
      out += u'станция отправления: %s <br>' % train['station0']
      out += u'станция прибытия: ' + train['station1'] + '<br>'
      out += u'время в пути: ' + train['timeInWay'] + '<br>'
      out += u'время отправления: ' + train['time0'] + '<br>'
      out += u'время прибытия: ' + train['time1'] + '<br>'
      bFirm = ''
      if 'bFirm' in train:
        bFirm = redFont0 + u' (фирменный)' + redFont1
      out += u'номер поезда: ' + train['number'] + bFirm + '<br>'
      for car in train['cars']:
        out += '---------------------<br>'
        out += u'тип: ' + car['typeLoc'] + '<br>'
        out += u'свободных мест: ' + str(car['freeSeats']) + '<br>'
        out += u'цена: ' + str(car['tariff']) + '<br>'
        out += '---------------------<br>'
  else:
    out += "Some error occured: " + str(r)

  s.response.out.write(out)

class MainPage(webapp2.RequestHandler):
  
  def get(self):
    global mainPage
    if not mainPage:
      mainPage = getMainPage()
    self.response.out.write(mainPage)

def getProperDate(date):
  items = date.split('/')
  sOut = ''
  try:
    sOut = ('%s.%s.%s' % (items[1], items[0], items[2]))
  except (IndexError):
    logging.error('IndexError: ' + date)
  return sOut

class TrainListPage(webapp2.RequestHandler):
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

  def post(self):
      self.response.out.write('<html><body>Результаты поиска:<pre>')
      st0  = cgi.escape(self.request.get('from'))
      storage.addReq(st0)
      st1  = cgi.escape(self.request.get('to'))
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

            if station in suggestDict:
              self.response.out.write(suggestDict[station])
              return

            req='http://pass.rzd.ru/suggester?lang=ru&stationNamePart='+urllib.quote(station.encode('utf-8'))
            respData = getResponse(req)

            if len(respData) > 0:
              rJson = json.loads(respData)
              suggOut = '['
              cnt = 1
              sStations = set()
              for item in rJson:
                if item['name'] not in sStations:
                  sStations.add(item['name'])
              lStations = self.sort4Find(sStations, station.lower())[:15]
              for item in lStations:
                  suggOut += '{\"id\":\"'+str(cnt)+'\",\"label\":\"'+item+'\",\"value\":\"'+item+'\"},'
                  cnt += 1
              suggOut = suggOut[:-1]
              suggOut += ']'

            if len(suggestDict) < suggestDictSize: #one more stub !!!
              suggestDict[station] = suggOut

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

class SummaryMailPage(webapp2.RequestHandler):

  def get(self):
    #sendMail(storage.getReq())
    pass

class TestPage(webapp2.RequestHandler):

  def get(self):
      #resp = opener.open('http://pass.rzd.ru/suggester?lang=ru&stationNamePart=%D0%B9%D0%B9%D0%B9')
      #sendMail()
      #self.response.out.write(resp.read())
      #global suggestDict
      #for k in suggestDict.keys():
      #  self.response.out.write(k+'<br>')
      #storage.addUser('test@email.me')
      self.response.out.write(storage.getReq())

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/trains', TrainListPage),
    ('/suggester', SuggesterPage),
    ('/summary_mail', SummaryMailPage),
    ('/test', TestPage)
], debug=True)

#def main():
#    application.run()

#if __name__ == "__main__":
#    main()