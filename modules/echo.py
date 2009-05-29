"""Repeats any input sent to the bot. This is a catch all for testing purposes only and should never actually be used."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
RULE=r'.*'
PRIORITY=9999
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	bot.mesg(text,args[1])
	return False
