"""Given a query, returns a snooty google search for you"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
RULE=r'lmgtfy\s+.*'
PRIORITY=9999
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
import re, urllib.parse
def PROCESS(bot, args, text):
    q='lmgtfy '.join(text.split('lmgtfy ')[1:])
    q=urllib.parse.urlencode({'q':q}) 
    bot.mesg('http://lmgtfy.com/?'+q,args[1])
    return False
