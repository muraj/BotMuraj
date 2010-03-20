"""A mathematical catch-all.  Does not do unit conversion."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
RULE=r'.*'
PRIORITY=450
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
safe_dict = dict( [ (k, getattr(math, k)) for k in dir(math)[4:] ])
safe_dict['abs'] = abs
def func():
    return safe_dict.keys()
safe_dict['func'] = func
def PROCESS(bot, args, text):
    try:
        x = eval(text, {'__builtins__':None}, safe_dict)
    except:
        return True
    bot.mesg(text+' = '+str(x), args[1])
    return False
