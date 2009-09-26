"""This module records the last time a user was seen active by nick.  Users can query this by private messaging me with 'seen [nick]' where nick is a comma seperated list of nicks to return."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
RULE=r'.*'
PRIORITY=-9999
COMMAND='PRIVMSG'
DIRECTED=3	#Can be either directed or not
users = {}
def PROCESS(bot, args, text):
	last_seen = lambda x,y: u"%s at %s" % (x, y.ctime())
	if text.startswith('seen') and args[1]==args[-1]:
		ag = text.split()
		if len(ag) > 1:
			for u in ag[1].split(','):
				if not u in users:
					bot.mesg(u"%s is unknown" % (u), args[-1])
				else: bot.mesg(last_seen(u,users[u]), args[-1])
		else:
			for u,i in users.iteritems():
				bot.mesg(last_seen(u,i), args[-1])
		return False
	users[args[-1]] = datetime.now()
	return True
