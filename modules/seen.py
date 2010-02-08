"""This module records the last time a user was seen active by nick.  Users can query this by messaging me with 'seen [nick]' where nick is a comma seperated list of nicks to return."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import re
RULE=r'.*'
PRIORITY=-9999
COMMAND='PRIVMSG'
DIRECTED=3	#Can be either directed or not
users = {}
def last_seen(x, y, c, z):
	if type(x) != unicode: x = x.decode('utf-8')
	if type(y) != unicode: y = y.decode('utf-8')
	t=datetime.now()-z
	weeks,days=divmod(t.days,7)
	minutes,seconds=divmod(t.seconds,60)
	hours,minutes=divmod(minutes,60)
	fuzzy=filter(lambda x: x[1]!=0, [('week(s)',weeks),('day(s)',days),('hour(s)',hours),('minute(s)',minutes),('second(s)',seconds)])[0]
	return u"I saw %s as \"%s\" about %d %s ago %s." % (x, y, fuzzy[1], fuzzy[0], c)
def PROCESS(bot, args, text):
	if text.startswith('seen'):
		ag = text.split()
		if len(ag) > 1:
			for u in ag[1].split(',')[:5]:
				u=re.sub(r'[\.?!]','',u)
				if not u in users:
					bot.mesg(u"\"%s\" is unknown" % (u.decode('utf-8')), args[1])
				else: bot.mesg(last_seen(u,users[u][1],users[u][2],users[u][0]), args[1])
		else:
			for u,i in users.iteritems():
				bot.mesg(last_seen(u,i[1],i[2],i[0]), args[-1])
		return False
	users[args[-2].lower()] = (datetime.now(), args[-1], u'in channel '+args[1] if args[1] != args[-1] else 'when he talked to me')
	return True
