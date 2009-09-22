"""Joins an irc channel given the following syntax: 'join #chan' """
#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
RULE='^join\s#[^\s,]+'
PRIORITY=-10
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
def PROCESS(bot, args, text):
	chans=re.search(r'((#[^\s,]+),?)+', text)
	if not chans:
		bot.mesg('Channel not found', args[1])
		return False
	chans=chans.group(0).split(',')
	for chan in chans:
		if chan in bot.chans:
			bot.mesg("Channel %s already joined." % chan, args[1])
		else:
			bot.joinchan(chan)
			bot.mesg("Channel %s joined" % chan, args[1])
	return False
