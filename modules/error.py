"""This module raises an error within the bot. This modules is purely for testing/debugging purposes of the internals of the bot only."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
RULE=r'^error$'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	raise Exception('OMG! ERROR!!')
