import aiml.Kernel
from time import sleep
alice=aiml.Kernel()
bob=aiml.Kernel()
alice.verbose(False)
bob.verbose(False)
alice.loadBrain('./aiml/IRCBot.brn')
alice.setBotPredicate('name','Alice')
alice.setPredicate('name','Bob')
bob.loadBrain('./aiml/IRCBot.brn')
bob.setBotPredicate('name','Bob')
bob.setPredicate('name','Alice')

str='Are you alive?'
print '**INITALIZER:',str
while(1):
	str=bob.respond(str.replace(',',' '))
	print 'Bob:',str
	sleep(1)
	str=alice.respond(str.replace(',',' '))
	print 'Alice:',str
	sleep(1)
