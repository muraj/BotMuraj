"""Dancing Bots!  OMG! Try parameters 'once' 'twice' 'thrice' or a number < 10"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import random
RULE=r'(?i)^dance((\s(once|twice|thrice|\d+))|())'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
dancers=[
		'\o/ ',
		' |  ',
		'/ \ ',
		'\o  ',
		' |\ ',
		'/ \ ',
		' o/ ',
		'/|  ',
		'/ \ ',
		'o// ',
		' |  ',
		'//  ',
		'\\\\o ',
		' |  ',
		' \\\\ ', 
		'\\\\o ',
		' |  ',
		'//  ',
		'o// ',
		' |  ',
		' \\\\ ',
		'_o_',
		' | ',
		'/ \\',
		'_o/',
		' | ',
		'/ \\',
		'\\o_',
		' | ',
		'/ \\',
		'_o_',
		' | ',
		'// ',
		'_o_',
		' | ',
		' \\\\',
		'\\o_',
		' | ',
		'// ',
		'\\o_',
		' | ',
		' \\\\',
		'_o/',
		' | ',
		'// ',
		'_o/',
		' | ',
		' \\\\',]
def PROCESS(bot, args, text):
	num=re.search(r'(?i)^dance((\s(once|twice|thrice|\d+))|())',text)
	str1, str2, str3='','',''
	if not num:
		return True
	try:
		num={'':1,'once':1,'twice':2,'thrice':3}[num.group(1).strip()]
	except:
		num=int(num.group(1).strip())
	num=min(num,10)
	for dumb in xrange(num):
		i=int((len(dancers)/3)*random.random())
		str1+=dancers[i*3]+' '
		str2+=dancers[i*3+1]+' '
		str3+=dancers[i*3+2]+' '
	bot.mesg(str1,args[1])
	bot.mesg(str2,args[1])
	bot.mesg(str3,args[1])
	return False

if __name__=='__main__':
	PROCESS(None,None,'dance 10')
