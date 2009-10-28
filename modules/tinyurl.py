"""Listens for long URLs ( > 45 characters) and prints a shorter URL using tinyurl's api.  Usage: http://[url]/  or  PM the bot to send a link to a channel with the syntax: tinyurl #chan http://[url]/"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, re, socket, sys, htmllib, httplib, os.path
from xml.etree.ElementTree import ElementTree, dump, SubElement, Element	#ElementTree is my new best friend
from time import localtime, strftime

RULE=r'(?i).*\b(http:\/\/\S+).*'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=3	#Can both be directed and not
MINSIZE=60
TINYURL='http://tinyurl.com/api-create.php?'
USE_RSS=True
RSS_FILEPATH=os.path.abspath('/home/cperry/pub/feed.xml')
RSS_TITLE='CSC Link Dump'
RSS_LINK='http://vr.nmu.edu/~cperry/'
RSS_DATEFORMAT='%a, %d %b %Y %T %z'
RSS_MAX=5
class Opener(urllib.FancyURLopener):
	version='Mozilla/5.0'
def PROCESS(bot, args, text):
	global TINYURL
	urllib._urlopener=Opener()	#Changes the user-agent to Mozilla
	groups=re.search(r'\b(http:\/\/\S+)',text)
	if not groups:
		return True
	else: url=groups.group(0)
	try:
		mime,title=getUrl(url)
	except Exception as e:
		bot.log(e,'warning')
	if len(title)>50: title=title[:47]+'...'
	try:
		if USE_RSS: sendToRSS(url,title,args[-1])
	except Exception as e:
		bot.log("Error sending to rss feed: %s" % (e),'error')
	if len(url) < MINSIZE and (not text.startswith('tinyurl ')): return True
	try:
		returl=getTiny(url)
	except Exception as e:
		bot.log("Error getting tinyurl: %s" % (e),'error')
		return False
	if text.startswith('tinyurl ') and args[1][0]!='#':
		chan=text.split(' ')
		if len(chan) == 3: chan=chan[1]
		if chan[0]=='#':
			if not chan in bot.chans:
				bot.mesg("I have not joined that channel.", args[1])
				return False
			bot.mesg("%s posted: %s \"%.*s...\"" % (args[-1], returl, 50, title), chan)
			return False
	bot.mesg("Tiny: \x02\x1F%s\x0F \"%s\"" % (returl, title ), args[1])
	return False
def getUrl(url):
	"""Returns the (MIME, title) of a url where title is the <title>[content]</title> in html"""
	title, mime="N/A", "N/A"
	socket.setdefaulttimeout(3)
	try:
		f=urllib.urlopen(url)
		mime = f.info().subtype
		if not mime == 'html': return mime, title
		html=f.read(8096)	#Should grab most titles
		group=re.search(r'(?i)(?:\<title\>)(.*)(?:\<\/title\>)',html, re.DOTALL)
		if not group: return mime, title
		title=unicode(group.group(1),'utf-8')
		for k, v in htmllib.HTMLParser.entitydefs.iteritems():
			if not v.startswith('&#'):
				title=title.replace('&%s;' % k,unicode(v,'latin-1'))
			else: title=title.replace('&%s;' % k, v)
		title=re.sub(r'&#(\d+);',lambda m: unichr(int(m.group(1))),title)
		title=title.replace('\n','').replace('\r','')
		title=title.strip()
	except Exception as e: raise e
	finally:
		f.close()
		socket.setdefaulttimeout(10)
	return mime, title
def getTiny(url):
	"""Returns the TinyURL version of <url>"""
	tinyurl="N/A"
	try:
		param=urllib.urlencode({'url':url})
		f=urllib.urlopen("%s%s" % (TINYURL, param))
		ret=f.read().rstrip()
		if re.match(r'(?i)^(http:\/\/\S+)$',ret): tinyurl=ret
		else: raise Exception("Bad URL returned: %s" % (ret))
	except Exception as e: raise e
	finally:
		if f: f.close()
	return tinyurl
def setupFeed():
	link=RSS_LINK+os.path.split(RSS_FILEPATH)[1]
	template="""\
<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" title="CSS_formating" href="rss.css" ?>
<?xml-stylesheet type="text/xsl" href="rss.xsl" ?>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>%s</title>
<link>%s</link>
<description>blah</description>
<language>en-us</language>
</channel>
</rss>
""" % (RSS_TITLE,link)
	f=open(RSS_FILEPATH,'w')
	f.write(template)
	f.close()
def sendToRSS(url, title, poster):
	"""Appends the url to the rss feed"""
	if url == RSS_LINK+os.path.split(RSS_FILEPATH)[1]: return
	if not os.path.exists(RSS_FILEPATH): setupFeed()
	e=ElementTree()
	e.parse(RSS_FILEPATH)
	chan=e.find('channel')
	r=[]
	for i,it in enumerate(chan.getiterator('item')):
		if it.find('guid').text == url:
			it.find('pubDate').text=strftime(RSS_DATEFORMAT,localtime())
			chan.remove(it)		#Keep in sorted order
			chan.insert(5,it)
			break
		elif i>RSS_MAX: r.append(it)
	else:
		for it in r: chan.remove(it)
		it=Element('item')
		SubElement(it,'title').text=title
		SubElement(it,'link').text=url
		SubElement(it,'pubDate').text=strftime(RSS_DATEFORMAT,localtime())
		SubElement(it,'guid').text=url
		chan.insert(5,it)
	f=open(RSS_FILEPATH,'r+')
	f.write("""<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" title="CSS_formating" href="rss.css" ?>
<?xml-stylesheet type="text/xsl" href="rss.xsl" ?>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
""")
	e.write(f)
