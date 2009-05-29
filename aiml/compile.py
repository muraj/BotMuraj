#!/usr/bin/python
import Kernel
import sys
if __name__ == '__main__':
	k=Kernel.Kernel()
	if not len(sys.argv) > 1:
		print 'Usage: %s [test|build|learn file]' % sys.argv[0]
		exit(1)
	if sys.argv[1]=='test':
		k.loadBrain('./IRCBot.brn')
		while True:
			i=raw_input('> ')
			print k.getBotPredicate('name')+':', k.respond(i)
	elif sys.argv[1]=='build':
		k.learn('standard/*.aiml')
		k.learn('standard/BadAnswer.aiml')	#Learn this last!!
		if 'y' in raw_input('Save brain? [N/y]').lower():
			k.saveBrain('./IRCBot.brn')
	elif sys.argv[1]=='learn':
		try:
			k.loadBrain('./IRCBot.brn')
			k.learn(sys.argv[2])
			k.saveBrain('./IRCBot.brn')
		except:
			print 'Usage: %s [test|build|learn file]'
