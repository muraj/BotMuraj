"""How big is your epenis? On 'uptime' or 'penis' gives bot uptime and ascii art penis"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import commands
import os
import re
RULE = r'^(uptime)|(penis)$'
PRIORITY = -9999
COMMAND='PRIVMSG'
DIRECTED=True
#### CONFIGURATION
SCALE = 80.0/31556926.0
UNITS = ['second(s)','minute(s)','hour(s)','day(s)','month(s)','year(s)']
SECPERUNIT = [ 1, 60, 3600, 86400, 2629743.83, 31556926]
####
def PROCESS(bot, args, text):
	global SCALE, UNITS, SECPERUNIT
	o=commands.getoutput("ps -o etime %d" % os.getpid())
	times=map(int,re.findall(r'(\d+)',o))
	times.reverse()
	s=0
	for i,d in enumerate(times):
		s+=d*SECPERUNIT[i]
		times[i]="%d %s" % (d, UNITS[i])
	times.reverse()
	bot.mesg("I\'ve been up for %s and %s!" % (' '.join(times[:-1]), times[-1]), args[1])
	if text=='penis':
		shaft=chr(3)+'138='
		for i in xrange(0,int(s*SCALE)): shaft+='='
		shaft+='D'
		bot.mesg(shaft, args[1])
	return False
