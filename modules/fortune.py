"""On the first word 'fortune', displays output from 'fortune -s'"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import sys
RULE=r'^fortune\b.*'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
def PROCESS(bot, args, text):
	reply=subprocess.check_output(['fortune','-s'])
	reply=reply.replace('\t','   ').replace('\n',' ')
	bot.mesg(reply, args[1])
	return False
