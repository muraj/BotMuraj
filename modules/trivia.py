"""Trivia questions!  Type 'trivia' to start a question.  Scores are recorded by user, not by nick.  To see your score, type 'trivia scores'"""
import random
import threading
import sqlite3
###GLOBALS
RULE1 = r'(?i)^trivia(\sscores)?' #Start game state
RULE2 = r'.*'	#Recieve Answer state
TIMER=60 #seconds
TIMER_EVENT=threading.Event()
SCORES={}
CON = sqlite3.connect('modules/triviadb')
ANSWER = []
###MODULE GLOBAL DEFINES
RULE=RULE1
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True

class timer(threading.Thread):
	event=None
	def __init__(self, event, bot, answer, chan):
		threading.Thread.__init__(self)
		self.event=event
		self.bot=bot
		self.answer = answer
		self.chan = chan
	def run(self):
		global TIMER
		self.event.wait(TIMER)
		if not self.event.isSet():		#No one has answered yet and time is up!
			self.bot.mesg("Time\'s up!  The answer was \"%s\"." % ' or '.join(self.answer), self.chan)
			self.event.set()
def PROCESS(bot, args, text):
	global TIMER, TIMER_EVENT, RULE, PRIORITY, RULE2, ANSWER
	if not args[1] == '#trivia': return True	#Keep to only #trivia
	#if not args[1].startswith('#'): return True	#Prevent private messages
	if text == 'trivia scores':
		outScores(bot, args[1])
		return False
	if (TIMER_EVENT.isSet()) and RULE == RULE2:	# Only time this is clear is if the previous game is over.
		reset()
		TIMER_EVENT.clear()
	if RULE == RULE2:
		for ans in ANSWER:
			if text.lower() == ans.lower():
				global SCORES
				bot.mesg("That is correct! The answer was \"%s\". 1 point was awarded to %s." % (ans, args[-2]), args[1], args[-1])
				if SCORES.has_key(args[-2]): SCORES[args[-2]] += 1
				else: SCORES[args[-2]]=1
				TIMER_EVENT.set()
				reset()
				break
		else: print ANSWER, "GUESS:", text	#Debug answer
	elif text == 'trivia':
		q, ANSWER = getQ()
		answer_state()
		bot.mesg("OKAY! Answer this question in %d seconds:" % (TIMER), args[1])
		bot.mesg(q, args[1])
		TIMER_EVENT.clear()
		timer(TIMER_EVENT, bot, ANSWER, args[1]).start()
	return False
def outScores(bot, chan):
	global SCORES
	i=10
	bot.mesg('### TOP SCORES ###', chan)
	for k,v in SCORES.iteritems():
		if i==0: break
		bot.mesg("%-10s %d" % (k, v), chan)
		i=i-1
def getQ():
	global CON
	r = CON.execute('select * from trivia order by Random() limit 1')
	r = r.fetchone()
	b = [a.strip() for a in r[1].split('|')]
	return [ r[0], b ]
def reset():
        global RULE, RULE1, PRIORITY, DIRECTED
        RULE=RULE1
        PRIORITY=0
        DIRECTED=True
def answer_state():
	global RULE, RULE2, PRIORITY, DIRECTED, TIMER_EVENT
	RULE=RULE2
	PRIORITY=-10
	TIMER_EVENT.clear()
