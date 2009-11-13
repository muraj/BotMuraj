#!/usr/bin/python
import aiml, BayesBot.bayes, StringIO
from xml.etree import ElementTree as ET

def learnResponse(res, topic, input):
	"""Returns a file pointer with a full xml script to learn off of
	with the topic, input, and response"""
	root = ET.Element('aiml')
	t = ET.SubElement(root,'topic')
	t.set('name',topic)
	cat = ET.SubElement(t,'category')
	ET.SubElement(cat,'pattern').text = input.upper() 	#Normalize this...
	ET.SubElement(cat,'template').text = res			#Normalize this?
	s = StringIO.StringIO(u'')
	s.write('<?xml version="1.0" encoding="UTF-8" ?>')
	ET.ElementTree(root).write(s,'utf-8')
	s.seek(0,0)	#Reset the pointer for reading again
	return s

AIMLBrain=aiml.Kernel()
AIMLBrain.learnFiles('aiml/standard/*.aiml')
AIMLBrain.learnFiles('aiml/standard/Badanswer.aiml')
TopicBrain=bayes.Bayes()
TopicBrain.load('bayes.bay')
while 1:
	s=raw_input('> ')
	if s == '': continue
	currentTopic = AIMLBrain.getPredicate('topic')
	if not 'unknown' in currentTopic.lower():
		print "BAYES: Changing topic"
		AIMLBrain.setPredicate('topic', TopicBrain.guess(s)[0])
	resp=AIMLBrain.respond(s)
	if resp == '':
		AIMLBrain.setPredicate('topicthat', AIMLBrain.getPredicate('topic'))
		AIMLBrain.setPredicate('topic', 'UNKNOWN')
		print AIMLBrain.getPredicate('topic'),'>>', AIMLBrain.respond(s)
	else:
		print AIMLBrain.getPredicate('topic'),'>>', resp
	if 'unknown' in currentTopic.lower() and not 'unknown' in AIMLBrain.getPredicate('topic').lower():
		print AIMLBrain.getPredicate('_inputHistory')
		#We just left the learning state
		topic = AIMLBrain.getPredicate('topic')
		input = AIMLBrain.getPredicate('learn_input')
		while 1:	#Learn until you get it right.
			t=TopicBrain.guess(input)
			if t[0] == topic.encode('utf-8').upper(): break
			TopicBrain.train(topic, input)
		if AIMLBrain.getPredicate('learn_resp') != '': #Learning a new response too?
			f=learnResponse(s,topic,input)
			AIMLBrain.learn(f)
			if not f.closed: f.close()
			#AIMLBrain.save(FILENAME)
