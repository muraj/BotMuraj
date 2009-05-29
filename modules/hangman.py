"""Play Hangman!  Start the game with 'hangman' and type letters or a word to solve the puzzle. You have 20 seconds per letter!"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import random
RULE=r'(?i)^hangman$'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
#### CONFIGURATION
TIMER = 20		#User has 10 seconds (1 minute) to get the next letter
lynch = [ '  __  ',
	  ' |  | ',
	  '    | ',
	  '    | ',
	  '____|___',
	  '']
man = 'o|\\//\\'
#### GLOBALS
starttime = 0
word = ''
wrong = 0
letters = 'abcdefghijklmnopqrstuvwxyz'
answer = ''
current_chan = ''
current_user = ''
running = False
####
def PROCESS(bot, args, text):
	global starttime, word, letters, wrong, answer, current_chan, current_user, RULE, PRIORITY, running
	if time.time() - starttime > TIMER and running:
		bot.mesg('Time\'s up! Hangman is starting over!', current_chan)
		finish()
		return current_user != args[-1]
	if RULE == r'(?i)^hangman$':
		RULE = r'^[A-Za-z]+$'
		PRIORITY = -50
		starttime = time.time()
		word = pick_word()
		wrong = 0
		current_chan, current_user = args[1], args[-1]
		letters = 'abcdefghijklmnopqrstuvwxyz'
		answer=''.join(['_ ' for c in word])
		bot.mesg('Ok! You have 20 seconds per letter!', args[1])
		send_game(bot, args[1])
		running = True
		return False
	starttime = time.time()
	if args[-1] != current_user or args[1] != current_chan:	#Continue parsing if another user or chan is trying to use the bot.  Don't allow another hangman game
		if text == 'hangman':
			bot.mesg('Some one is currently playing hangman at the moment, please wait until they have completed',args[1])
			return False
		else: return True
	if (len(text) > 1 and text.lower() != word) or (len(text) == 1 and (not text[0] in word)):
		wrong+=1		#Got it wrong
	elif len(text) > 1:		#Got the word
		bot.mesg("You win! The answer was \"%s\"" % word, args[1])
		finish()
		return False
	else:				#Got a letter
		if not text[0] in letters:
			bot.mesg("You chose this word already")
		for i, s in enumerate(word):
			if s == text[0]:
				answer=answer[:i*2]+s+answer[i*2+1:]
		if not '_' in answer:
			bot.mesg("You win! The answer was \"%s\"" % word, args[1])
			finish()
			return False
	letters=letters.replace(text[0],'_')
	if wrong > 5:
		bot.mesg("You failed!  The answer was \"%s\"" % word, args[1])
		finish()
		return False
	else: send_game(bot, args[1])
	return False
def finish():
	global RULE, PRIORITY, running
	RULE = r'(?i)^hangman$'
	PRIORITY = 0
	running = False
def send_game(bot, chan):
	global wrong, word, lynch, man, letters, answer
	bot.mesg(lynch[0], chan)
	bot.mesg(lynch[1]+answer, chan)
	str=lynch[2]
	if wrong > 0: str=str[:1]+man[0]+str[2:]
	if wrong > 2: str=str[:0]+man[2]+str[1:]
	if wrong > 3: str=str[:2]+man[3]+str[3:]
	bot.mesg(''.join(str), chan)
	str=lynch[3]
	if wrong > 1: str=str[:1]+man[1]+str[2:]
	bot.mesg(''.join(str)+letters, chan)
	str=lynch[4]
	if wrong > 4: str=str[:0]+man[4]+str[1:]
	if wrong > 5: str=str[:2]+man[5]+str[3:]
	bot.mesg(''.join(str), chan)
	bot.mesg(lynch[5], chan)
def pick_word():
	words=open('modules/hangman_list.txt','r').readlines()
	return words[random.randint(0,len(words)-1)].lower()
