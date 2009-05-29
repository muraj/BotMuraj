"""On keyword 'help', displays a list of available parameters to help. 'explain' followed by any one of these parameters will display the documentation associated with that module."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
RULE=r'^(explain\s.*)|(help)'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
def PROCESS(bot, args, text):
	words=text.split()
	if len(words)==1:
		names=''
		for s in bot.mods.itervalues():
			names+=', '.join(map(lambda x: x.__name__, s))+', '
		names=names[:-2]
		bot.mesg(__doc__,args[1])
		bot.mesg('Please type \'explain\' followed by one of these parameters for more information: %s' % names,args[1])
		return False
	for mlist in bot.mods.values():
		for m in mlist:
			if m.__name__ == words[1]:
				bot.mesg(m.__name__+': '+m.__doc__, args[1])
				return False
	return PROCESS(bot, args, 'help') #If not found, recurse to base case (no copy and paste!)
