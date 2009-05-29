"""MASTER USE ONLY - Reloads a particular module from ./modules directory.  Useful for testing purposes or quick changes without taking down your bot. Syntax: 'reload [modulename|all]'"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import imp
import sys
RULE=r'^reload [A-Za-z0-9]+$'
PRIORITY=-9999
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	if bot.master != args[-1]:
		bot.mesg('No, you can\'t tell me what to do.',args[1])
		return False
	else: bot.mesg('Anything for you!',args[1])
	imp.acquire_lock()
	if text[7:]==__name__:
		bot.mesg('don\'t reload "reload" module!',args[1])
		return False
	found=True	#I hate python for/else statements...
	for k, mods in bot.mods.iteritems():
		for i, mod in enumerate(mods):
			if mod.__name__==text[7:] or text[7:]=='all':
				del mods[i] #COMMAND could have changed, so delete it from the dict
				bot.addhook(bot.modimport(text[7:]))
				break
		else: continue
		break
	else:
		found=False
	try:
		if text[7:]!='all' and not found:
			bot.addhook(bot.modimport(text[7:]))
	except ImportError as e:
		bot.mesg(''+e,args[1])
		print >> sys.stderr, 'RELOAD EXCEPTION:',e
	finally:
		imp.release_lock()
		for k,l in bot.mods.iteritems():
			bot.mods[k]=sorted(l, lambda m1,m2: m1.PRIORITY-m2.PRIORITY)
		bot.mesg("RELOADED MODULE: %s" % text[7:], args[1])
		return False
