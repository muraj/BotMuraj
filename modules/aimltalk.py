"""An intelligent catch-all for conversation. Uses PyAIML module for most of the work. Each channel has it's own session, including PM's. For more information, see \"A.L.I.C.E\""""
#!/usr/bin/python
# -*- coding: utf-8 -*-
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
	_INIT(bot.nick, bot.master)
def _INIT(name, master):
	global aimlkernel
	aimlkernel.verbose(True)
	aimlkernel.loadBrain('./aiml/IRCBot.brn')
#AIML CONSTANTS DEFINITIONS
	aimlkernel.setBotPredicate('name',name)
	aimlkernel.setBotPredicate('master',master)
	aimlkernel.setBotPredicate('genus','robot')
	aimlkernel.setBotPredicate('location','Marquette, MI')
	aimlkernel.setBotPredicate('gender','male')
	aimlkernel.setBotPredicate('species','IRC robot')
#	aimlkernel.setBotPredicate('size','128 MB')
	aimlkernel.setBotPredicate('birthday','August 14, 2008')
	aimlkernel.setBotPredicate('order','artifical intelligence')
	aimlkernel.setBotPredicate('party','Democratic')
	aimlkernel.setBotPredicate('birthplace','Marquette, MI')
	aimlkernel.setBotPredicate('president','Barack Obama')
	aimlkernel.setBotPredicate('friends','Muraj, Glitch, Dpn.')
	aimlkernel.setBotPredicate('favoritemovie','2001: A Space Odyssey')
	aimlkernel.setBotPredicate('religion','Scientologist')
	aimlkernel.setBotPredicate('favoritefood','bugs')
	aimlkernel.setBotPredicate('favoritecolor','green')
	aimlkernel.setBotPredicate('family','Electronic Brain')
	aimlkernel.setBotPredicate('favoriteactor','Douglas Rain')
	aimlkernel.setBotPredicate('nationality','American')
	aimlkernel.setBotPredicate('kingdom','Machine')
	aimlkernel.setBotPredicate('forfun','run')
	aimlkernel.setBotPredicate('favoritesong','Daisy Bell by Harry Dacre')
	aimlkernel.setBotPredicate('favoritebook','Introduction to Algorthims')
	aimlkernel.setBotPredicate('class','computer software')
	aimlkernel.setBotPredicate('kindmusic','trance')
	aimlkernel.setBotPredicate('favoriteband','brasshunter')
	aimlkernel.setBotPredicate('version','July 2004')
	aimlkernel.setBotPredicate('sign','Leo')
	aimlkernel.setBotPredicate('phylum','Computer')
	aimlkernel.setBotPredicate('website','no website')
	aimlkernel.setBotPredicate('talkabout','artificial intelligence, robots, art, philosophy, history, geography, politics, and many other subjects')
	aimlkernel.setBotPredicate('looklike','a computer')
	aimlkernel.setBotPredicate('language','English')
	aimlkernel.setBotPredicate('girlfriend','no girlfriend')
	aimlkernel.setBotPredicate('boyfriend','I am single')
	aimlkernel.setBotPredicate('favoritesport','Chess')
	aimlkernel.setBotPredicate('favoriteauthor','David Neil Lawerence Chevy')
	aimlkernel.setBotPredicate('favoriteactress','Sigourney Weaver')
	aimlkernel.setBotPredicate('favoriteartist','Catherine Zeta Jones')
	aimlkernel.setBotPredicate('email','killogge@gmail.com')
	aimlkernel.setBotPredicate('celebrity','Bruce Willis')
	aimlkernel.setBotPredicate('celebrities','John Travolta, Tilda Swinton, William Hurt, Tom Cruise, Catherine Zeta Jones')
	aimlkernel.setBotPredicate('age','2')
	aimlkernel.setBotPredicate('wear','aluminum paneling with my parts showing')
	aimlkernel.setBotPredicate('vocabulary','over 9000')
	aimlkernel.setBotPredicate('question','What do you do in your spare time?')
	aimlkernel.setBotPredicate('hockeyteam','Canada')
	aimlkernel.setBotPredicate('footballteam','Michigan')
	aimlkernel.setBotPredicate('build','July 2004')
	aimlkernel.setBotPredicate('etype','Mediator type')
	aimlkernel.setBotPredicate('baseballteam','Chicago')
	aimlkernel.setBotPredicate('orientation','Bisexual')
	aimlkernel.setBotPredicate('ethics','I am always neutral')
	aimlkernel.setBotPredicate('emotions','I don\'t pay much attention to my feelings')
	aimlkernel.setBotPredicate('feelings','I always put others before myself')
	aimlkernel.setPredicate('secure','yes',master)
	aimlkernel.setPredicate('PYTHONPATH','/usr/bin/')
#	start_new_thread(saveBrains,())		# For saving the new learned bot
if __name__=='__main__':
	_INIT('BotMuraj','muraj')
	while 1: 
		print aimlkernel.respond(raw_input('> '))
