"""An intelligent catch-all for conversation. Uses PyAIML module for most of the work. Each channel has it's own session, including PM's. For more information, google \"A.L.I.C.E\""""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import Bayes, StringIO
from xml.etree import ElementTree as ET
import aiml
RULE=r'.*'
PRIORITY=500
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
aimlkernel=aiml.Kernel()
BayesBrain = Bayes.Bayes()

def learnResponse(res, topic, input):
	"""Returns a file pointer with a full xml script to learn off of
	with the topic, input, and response"""
	root = ET.Element('aiml')
	t = ET.SubElement(root,'topic')
	subber = aiml.WordSub.WordSub(aiml.DefaultSubs.defaultNormal)
	topic = subber.sub(topic).upper()
	t.set('name',topic)
	cat = ET.SubElement(t,'category')
	ET.SubElement(cat,'pattern').text = subber.sub(input).upper()   #Normalize this.
	ET.SubElement(cat,'template').text = res            #Kinda normalize this.
	s = StringIO.StringIO(u'')
	s.write('<?xml version="1.0" encoding="UTF-8" ?>')
	ET.ElementTree(root).write(s,'utf-8')
	s.seek(0,0) #Reset the pointer for reading again
	return s

def PROCESS(bot, args, text):
	global aimlkernel
### Text replacements
	text=text.replace('\x01ACTION','I')	#To replace actions sent in irc
	text=text.replace(bot.nick,'you')	#Make into a direct conversation.
	text=text.replace('\x01','')		#Remove irc syntax
###
	aimlkernel.setPredicate('name', args[-1], args[1])
	currentTopic = aimlkernel.getPredicate('topic')
	if not 'unknown' in currentTopic.lower():
		aimlkernel.setPredicate('topicthat',currentTopic)	#In case of a correct topic and bad answer, set the current topic
		aimlkernel.setPredicate('topic',BayesBrain.guess(text)[0])	#Guess the new topic
	resp = aimlkernel.respond(text)
	bot.mesg(resp,args[1],args[-1])
	if 'unknown' in currentTopic.lower() and not 'unknown' in aimlkernel.getPredicate('topic').lower() and text.lower() != 'nevermind':	#Needs to be fixed better.
		#Getting out of the user side of the learning
		topic = aimlkernel.getPredicate('topic')
		input = aimlkernel.getPredicate('learn_input')
		while 1:
			BayesBrain.train(topic, input)
			if BayesBrain.guess(input)[0] == topic.encode('utf-8').upper(): break
		BayesBrain.save('Bayes/bayes.bay')	# Untested...
		if aimlkernel.getPredicate('learn_resp') != '':
			f=learnResponse(text, topic, input)
			bot.log('Learned - '+f.getvalue(),'debug')
			aimlkernel.learn(f)
			aimlkernel.saveBrain('aiml/IRCBot.brn')
			if not f.closed: f.close()
	return False
def INIT(bot):
	_INIT(bot.nick, bot.master, bot.config)
def _INIT(name, master, config=None):
	global aimlkernel, BayesBrain
	import os.path
	notPredicates = ['aimlbrain', 'bayesbrain', 'secure', 'name', 'master']
	aimlkernel.verbose(True)
	aimlkernel.loadBrain(os.path.abspath(config.get('aimltalk','aimlbrain')))
	BayesBrain.load(os.path.abspath(config.get('aimltalk','bayesbrain')))
	aimlkernel.setPredicate('secure','yes',master)
	aimlkernel.setBotPredicate('name',name)
	aimlkernel.setBotPredicate('master',master)
	aimlkernel.setPredicate('topic','Greeting')
	aimlkernel.setPredicate('topicthat','Greeting')
	for var,val in config.items('aimltalk'):
		if var in notPredicates: continue
		aimlkernel.setBotPredicate(var,val)
if __name__=='__main__':
	_INIT('BotMuraj','muraj')
	while 1: 
		print aimlkernel.respond(raw_input('> '))
