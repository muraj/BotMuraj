#!/usr/bin/python
# -*- coding: utf-8 -*-
"""An intelligent catch-all for conversation. Uses PyAIML module for most of the work. Each channel has it's own session, including PM's. For more information, google \"A.L.I.C.E\" """
import aiml.Kernel
from thread import start_new_thread
from time import sleep
RULE=r'.*'
PRIORITY=500
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
aimlkernel=aiml.Kernel()
def PROCESS(bot, args, text):
	global aimlkernel
### Text replacements
	text=text.replace('\x01ACTION','I')	#To replace actions sent in irc
	text=text.replace(bot.nick,'you')
	text=text.replace('\x01','')
###
	aimlkernel.setPredicate('name', args[-1], args[1])
	response=aimlkernel.respond(text, args[1])
	length=len(response)
	cat=''
	if length>450:
		cat=' --'
	for i in xrange(0,length,450):
		if i+450>length:
			cat=''
		if args[-1]==args[1]:
			bot.mesg(response[i:i+450]+cat,args[1], args[-1])
		else: bot.mesg(response[i:i+450]+cat, args[1], args[-1])
	return False
def saveBrains():
	while True:
		sleep(3600)	#save every hour
		aimlkernel.saveBrain('./aiml/IRCBot.brn')
def INIT(bot):
	_INIT(bot.nick, bot.master, bot.config)
def _INIT(name, master, config=None):
	global aimlkernel
	aimlkernel.verbose(True)
	aimlkernel.loadBrain('./aiml/IRCBot.brn')
	if config==None: return
	if not config.has_section('aimltalk'): return
	aimlkernel.setPredicate('secure','yes',master)
	aimlkernel.setPredicate('PYTHONPATH',config.get('aimltalk','pythonpath'))
	aimlkernel.setBotPredicate('name',name)
	aimlkernel.setBotPredicate('master',master)
	for var,val in config.items('aimltalk'):
		aimlkernel.setBotPredicate(var,val)
if __name__=='__main__':
	_INIT('BotMuraj','muraj')
	while 1: 
		print(aimlkernel.respond(raw_input('> ')))
