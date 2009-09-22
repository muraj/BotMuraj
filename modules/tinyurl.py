"""Listens for long URLs ( > 45 characters) and prints a shorter URL using tinyurl's api.  Usage: http://[url]/  or  PM the bot to send a link to a channel with the syntax: tinyurl #chan http://[url]/"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import re
import socket
import sys
import htmllib
import httplib
#httplib.HTTPConnection.debuglevel = 0
RULE=r'(?i).*\b(http:\/\/\S+)\b.*'
PRIORITY=0
COMMAND='PRIVMSG'
MINSIZE=45
TINYURL='http://ze.nu/api-create.php?url='
=======
MINSIZE=60
TINYURL='http://tinyurl.com/api-create.php?url='
DIRECTED=3	#Can both be directed and not
class Opener(urllib.FancyURLopener):
	version='Mozilla/5.0'
def PROCESS(bot, args, text):
	global TINYURL
	urllib._urlopener=Opener()	#Changes the user-agent to Mozilla
	groups=re.search(r'\b(http:\/\/\S+)\b',text)
	if not groups:
		return True
	else: url=groups.group(0)
	if len(url) < MINSIZE and (not text.startswith('tinyurl ')): return True
	title="N/A"
	f=None
	try:
		socket.setdefaulttimeout(3)
		f=urllib.urlopen(url)
		if f.info().subtype == 'html':
			html=f.read(8096)	#Should grab most titles
			group=re.search(r'(?i)(?:\<title\>)(.*)(?:\<\/title\>)',html, re.DOTALL)
			if group:
				title=unicode(group.group(1),'utf-8')
				for k, v in htmllib.HTMLParser.entitydefs.iteritems():
					if not v.startswith('&#'): title=title.replace('&%s;' % k,unicode(v,'latin-1'))
					else: title=title.replace('&%s;' % k, v)
				title=re.sub(r'&#(\d+);',lambda m: unichr(int(m.group(1))),title)
				title=title.replace('\n','')
				title=title.strip()
			else:
				title="N/A"
		else: title=f.info().subtype
	except Exception as e:
		bot.log('Error reading title from url.', 'error')
	finally:
		if f != None:
			f.fp.close()
			f.close()
                        del f   #Feeble attempt to close active connections.
        f=None
	try:
		socket.setdefaulttimeout(10)
		f=urllib.urlopen("%s%s" % (TINYURL,  url))
		returl=f.read().rstrip()
		if not re.match(r'(?i)^(http:\/\/\S+)$', returl):
			bot.log("Bad url returned: %s" % (returl), 'warning')
			return False
	except Exception as e:
		bot.log('Cannot contact tinyurl!','critical')
		bot.mesg('Error contacting tinyurl.com', args[1])
		raise e
	finally:
		if f != None:
			f.fp.close()
			f.close()
                        del f
	if text.startswith('tinyurl ') and args[1][0]!='#':
		chan=text.split(' ')
		if len(chan) == 3: chan=chan[1]
		if chan[0]=='#':
			if not chan in bot.chans:
				bot.mesg("I have not joined that channel.",args[1])
			bot.mesg("%s posted: %s \"%.*s...\"" % (args[-1], returl, 50, title), chan)
			return False
	bot.mesg("Tiny: \x02\x1F%s\x0F \"%.*s...\"" % (returl, 50, title ), args[1])
	return False
