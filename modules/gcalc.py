"""Google Calculator for IRC! Syntax: \"gcalc <maths>\"."""
import re
import urllib
RULE=r'^gcalc (.+)$'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=True
class Opener(urllib.FancyURLopener):	#Needed to grab google searches (it doesn't like urllib user-agent)
	version='Mozilla/5.0'
def PROCESS(bot, args, text):
	str=re.search(r'^gcalc (.+)$', text)
	if not str:
		bot.mesg('No result', args[1])
		return False
	else: str=str.group(1)
	params = urllib.urlencode({'num': 1, 'q' : str.lower()})
	urllib._urlopener = Opener()
	f=urllib.urlopen("http://www.google.com/search?%s" % params)
	str=f.read()
	ret=re.search(r'<h2 class=r style="font-size:138%"><b>(.+)</b></h2>', str)
	f.close()
	if not ret:
		bot.mesg('No result', args[1])
		return False
	ret=re.sub(r'&#(\d+);',lambda m: unichr(int(m.group(1))),ret.group(1)) #html unicode parsing.
	ret=re.sub(r'<sup>(.*)</sup>', lambda m: "^(%s)" % m.group(1),ret)	#Until I get to unicode superscripts, etc.
	bot.mesg(ret, args[1])
	return False
