"""If kicked from a channel, this internal module will do the cleanup necessary for the bot"""
RULE=r'.*'
PRIORITY=-99999
COMMAND='KICK'
def PROCESS(bot, args, text):
	if args[2]==bot.nick:
		bot.log('KICKED! %s %s' % (args, text), 'warning')
		bot.chans.remove(args[1])
	return True
