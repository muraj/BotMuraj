"""Displays the weather using the following syntax: 'weather [zipcode|city, state]'"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
#from xml.dom import minidom
import xml.etree.ElementTree
RULE=r'^weather|forecast(\s\d{5}|\s[a-zA-z\.,\- ]*,\s*[A-Za-z]{2})?$'
HOME='Marquette, MI'
PRIORITY=-10
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed at
def PROCESS(bot, args, text):
	zip=text[8:]
	if not zip or zip=='': zip=HOME
	url=urllib.urlopen('http://www.google.com/ig/api?'+urllib.urlencode({'weather':zip}))
	try:
		strings=_process(url,zip,text.startswith('forecast'))
	except Exception as e:
		raise e
	finally: url.close()
	for s in strings:
		bot.mesg(s,args[1])
	return False
def _process(url,zip,forecast=True):
	str=[" "]
	try:
		e=xml.etree.ElementTree.parse(url)
	except:
		return ['Google returned a malformed xml']
	try:
		return ["Google returned the following error: %s" % (e.find('/weather/problem_cause').attrib['data'])]
	except: pass
	str.append("%s" % e.find('/weather/forecast_information/city').attrib['data'])
	day = e.find('/weather/current_conditions')
	fn=lambda x: day.find(x).attrib['data']
	temp=int(fn('temp_f'))
	hum=int(fn('humidity')[-4:-1])
	str.append(u"Temperature:\u0003%02d%3d\u00B0F\u000F Humidity:\u0003%02d%3d%%" % (color_temp(temp), temp, color_hum(hum), hum))
	wind=fn('wind_condition')
	chill=getWindChill(int(wind.split()[-2]),temp)
	str.append(u" Wind Chill:\u0003%02d%3d\u00B0F\u000F     %s" % (color_temp(chill), chill, wind))
	str.append("Current Conditions: %s" % fn('condition'))
	if not forecast: return str+[' ']	#Skip out
	for day in e.findall('/weather/forecast_conditions'):
		str.append(u"%s: %-18s \u000305%3s\u00B0F\u000F /\u000302%3s\u00B0F\u000F" % (fn('day_of_week'), fn('condition'), fn('high'), fn('low')))
	str.append(" ")
	return str
def INIT(bot):
	global HOME
	if bot.config.has_section('weather'):
		HOME=bot.config.get('weather','home')
def getWindChill(V, T):	#V=wind_speed, T=air_temp
	"""From the NWS website"""
	if V>5: return 35.74+0.6215*T-35.75*(V**0.16)+0.4275*T*(V**0.16)
	return T
def color_temp(t):
	"""Sends a color code based on temperature"""
	if   t > 80: return 5	#Red
	elif t > 50: return 8	#Yellow
	elif t > 20: return 12	#Light Blue
	else:        return 2	#Blue
def color_hum(t):
	"""Sends a color code based on humdity"""
	if   t > 75: return 3	#Green
	elif t > 50: return 9	#Light Green
	elif t > 30: return 0	#White
	else: return 8		#Yellow
