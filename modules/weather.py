"""Displays the weather using the following syntax: 'weather [zipcode]'"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
from xml.dom import minidom
import re
RULE=r'^weather(\s\d{5})?$'
PRIORITY=-10
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	print "here"
	zip=re.search('(\d{5})',text)
	if not zip: zip='49855'
	else: zip=zip.group(0)
	strings=_process(zip)
	for s in strings:
		bot.mesg(s,args[1])
	return False
def _process(zip):
	str=[]
	url=urllib.urlopen('http://www.google.com/ig/api?weather='+zip)
	doc=minidom.parse(url)
	info = doc.getElementsByTagName('forecast_information')[0]
	str.append("%s" % info.getElementsByTagName('city')[0].getAttribute('data'))
	day = doc.getElementsByTagName('current_conditions')[0]
	fn=lambda x: day.getElementsByTagName(x)[0].getAttribute('data')
	temp=int(fn('temp_f'))
	str.append(u"Temperature:%3d\u00B0F %s" % (temp, fn('humidity')))
	wind=fn('wind_condition')
	chill=getWindChill(int(re.search(r'(\d+)',wind).group(0)),temp)
	str.append(u" Wind Chill:%3d\u00B0F     %s" % (chill, wind))
	str.append("Current Conditions: %s" % fn('condition'))
	for day in doc.getElementsByTagName('forecast_conditions'):
		str.append(u"%s: %s\u000302%3s\u00B0F\u000F/\u000305%3s\u00B0F\u000F" % (fn('day_of_week'), fn('condition'), fn('low'), fn('high')))
	return str
def getWindChill(V, T):	#V=wind_speed, T=air_temp
	"""From the NWS website"""
	if V>5: return 35.74+0.6215*T-35.75*(V**0.16)+0.4275*T*(V**0.16)
	return T
