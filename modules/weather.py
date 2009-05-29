"""Displays the weather using the following syntax: 'weather [zipcode]'"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
from xml.dom import minidom
from decimal import *
import re
from time import asctime
RULE=r'^weather(\s\d{5})?$'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
### CONFIG VARS
CODE=['00,04Tornado','07Tropical Storm','14Hurricane','00,04Severe Thunderstorms','04Thunderstorms',
'09Mixed Rain and Snow','11Mixed Rain and Sleet','12Mixed Snow and Sleet',
'10Freezing Drizzle','15Drizzle','12Freezing Rain','14Showers','14Showers','12Snow Flurries',
'02Light Snow Showers','02Blowing Snow','00Snow','02Hail','12Sleet','08Dust','00Foggy','00Haze',
'14Smoky','02Blustery','11Windy','02Cold','11Cloudy','Mostly Cloudy (night)','Mostly Cloudy (day)',
'14Partly Cloudy (night)','14Partly Cloudy (day)','00Clear (night)','08Sunny','Fair (night)',
'Fair (day)','03Mixed Rain and Hail','05Hot','08Isolated Thunderstorms','08Scattered Thunderstorms',
'00,03Scattered Thunderstorms','09Scattered Showers','Heavy Snow','Scattered Snow Showers',
'00,02Heavy Snow','Partly Cloudy','09Thundershowers','11Snow Showers','09Isolated Thundershowers']
###
def PROCESS(bot, args, text):
	zip=re.search('(\d{5})',text)
	if not zip: zip='49855'
	else: zip=zip.group(0)
	strings=_process(zip)
	for s in strings:
		bot.mesg(s,args[1])
	return False
def _process(zip):
	global CODE
	str=[]
	url=urllib.urlopen('http://weather.yahooapis.com/forecastrss?p='+zip)
	doc=minidom.parse(url)
	error=doc.getElementsByTagName('title')[0]
	if 'error' in error.firstChild.data.lower():
		return ('City not found')
	loc=doc.getElementsByTagName('yweather:location')[0]
	lat=doc.getElementsByTagName('geo:lat')[0].firstChild.data
	long=doc.getElementsByTagName('geo:long')[0].firstChild.data
	str.append(u"%s, %s, %s (%s,%s)" % (loc.getAttribute('city'), loc.getAttribute('region'), loc.getAttribute('country'), lat, long))
	str.append(asctime())
	cond=doc.getElementsByTagName('yweather:condition')[0]
	temp=cond.getAttribute('temp')
	tempint=int(temp)
	if tempint>60: temp=chr(3)+u"04"+temp
	elif tempint<30: temp=chr(3)+u"02"+temp
	temp+=chr(15)
	forcast=doc.getElementsByTagName('yweather:forecast')
	str.append(u"      Temp: %3s\u00B0 F    Hi/Lo: \u000305%3s\u00B0 F\u000F/\u000302%3s\u000F\u00B0 F" % (temp, forcast[0].getAttribute('high'), forcast[0].getAttribute('low')))
	wind=doc.getElementsByTagName('yweather:wind')[0]
	dir=direction(Decimal(wind.getAttribute('direction')))
	chill=wind.getAttribute('chill')
	if chill=='': chill='0'
	str.append(u"Wind Chill: %3s\u00B0 F     Wind: %3smph %3s" % (chill, wind.getAttribute('speed'), dir))
	atmos=doc.getElementsByTagName('yweather:atmosphere')[0]
	hum=atmos.getAttribute('humidity')
	humint=int(hum)
	if humint > 50: hum=chr(3)+u'03'+hum+chr(15)
	elif humint < 20: hum=chr(3)+u'05'+hum+chr(15)
 	str.append(u"  Humidity: %3s%%   Pressure: %6.2f\"(%s)" % (hum, Decimal(atmos.getAttribute('pressure')), pressure(atmos.getAttribute('rising'))))
	astro=doc.getElementsByTagName('yweather:astronomy')[0]
	str.append(u"   Sunrise: %7s  Sunset: %7s" % (astro.getAttribute('sunrise').replace(' ',''), astro.getAttribute('sunset').replace(' ','')))
	code=int(cond.getAttribute('code'))
	str.append(u"Current Conditions: %s (%d)" % (chr(3)+CODE[code]+chr(15), code))
	code=int(forcast[0].getAttribute('code'))
	str.append(u"Today: %s, Highs \u000305%s\u00B0 F\u000F, Lows \u000302%s\u00B0 F\u000F" % (chr(3)+CODE[code]+chr(15), forcast[0].getAttribute('high'), forcast[0].getAttribute('low')))
	code=int(forcast[1].getAttribute('code'))
	str.append(u"%s: %s, Highs \u000305%s\u00B0 F\u000F, Lows \u000302%s\u00B0 F\u000F" % (forcast[1].getAttribute('day'), chr(3)+CODE[code]+chr(15), forcast[1].getAttribute('high'), forcast[1].getAttribute('low')))
	max = 0		#Centering
	for s in str:
		if max<len(str): max=len(str)
	str = [ s.center(max, ' ') for s in str ]
	doc.unlink()
	url.close()
	return str
def pressure(code):
	return {
		'0': 'Steady',
		'1': chr(3)+'05Rising'+chr(15),
		'2': chr(3)+'02Falling'+chr(15)
	}[code]
def direction(deg):
	while deg>360: deg-=360
	while deg<0: deg+=360
	if deg>348.75 or deg<=11.25: return 'N'
	if deg<=33.75: return 'NNE'
	if deg<=56.25: return 'NE'
	if deg<=78.75: return 'ENE'
	if deg<=101.25: return 'E'
	if deg<=123.75: return 'ESE'
	if deg<=146.25: return 'SE'
	if deg<=168.75: return 'SSE'
	if deg<=191.25: return 'S'
	if deg<=213.75: return 'SSW'
	if deg<=236.25: return 'SW'
	if deg<=258.75: return 'WSW'
	if deg<=281.25: return 'W'
	if deg<=303.75: return 'WNW'
	if deg<=326.25: return 'NW'
	else: return 'NNW'
if __name__=='__main__':
	print 'Example output:'
	for i in _process('49855'):
		print i
