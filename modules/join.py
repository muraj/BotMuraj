"""Joins an irc channel given the following syntax: 'join #chan' """
#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
RULE='^join\s#[A-Za-z0-9\-]+'
PRIORITY=-10
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	chan=re.search('#([A-Za-z0-9\-]+)', text)
	if not chan:
		bot.mesg('Channel not found', args[1])
		return False
	chan=chan.group(0)
	if chan in bot.chans:
		bot.mesg('Channel already joined.', args[1])
		return False
	bot.joinchan(chan)
	bot.mesg("Channel %s joined" % chan, args[1])
	return False
