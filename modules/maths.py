"""A mathematical catch-all.  Does not do unit conversion."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import math
from multiprocessing import Process, Queue
RULE=r'.*'
PRIORITY=450
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
TIMEOUT=2
safe_dict = dict( [ (k, getattr(math, k)) for k in dir(math)[4:] ])
safe_dict['abs'] = abs
def func():
    return safe_dict.keys()
safe_dict['func'] = func
def evalProc(queue, input):
	try:
		x = eval(input, {'__builtins__':None}, safe_dict)
		queue.put(x,True)
	except:
		pass
	return
def PROCESS(bot, args, text):
	global TIMEOUT
	q = Queue()
	p = Process(target=evalProc, args=(q,text))	#Setup a process that will run the eval.
	p.start()
	p.join(TIMEOUT)
	if not q.empty():
		bot.mesg(text+' = '+str(q.get(False)), args[1])
	else:
		p.terminate()	#Terminate the process if it took too long
		return True		#Fallback to lower priority subroutines
	return False
