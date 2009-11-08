"""Listens for long URLs and prints a shorter URL using tinyurl's api and acts as a link dump to an rss file.  Usage: http://[url] or PM the bot to send a link to a channel with the syntax: tinyurl #chan http://[url]"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, re, socket, sys, htmllib, httplib, os.path, codecs
from xml.etree.ElementTree import ElementTree, dump, SubElement, Element	#ElementTree is my new best friend
from time import localtime, strftime

RULE=r'(?i).*(http:\/\/\S+).*'
PRIORITY=0
COMMAND='PRIVMSG'
DIRECTED=3	#Can both be directed and not
MINSIZE=60
TINYURL='http://tinyurl.com/api-create.php?'
USE_RSS=False
RSS_FILEPATH=os.path.abspath('./feed.xml')
RSS_TITLE='CSC Link Dump'
RSS_LINK='http://localhost/'
RSS_DATEFORMAT='%a, %d %b %Y %T %z'
RSS_MAX=5
class Opener(urllib.FancyURLopener):
	version='Mozilla/5.0'
def PROCESS(bot, args, text):
	global TINYURL
	urllib._urlopener=Opener()	#Changes the user-agent to Mozilla
	groups=re.search(r'(http:\/\/\S+)',text)
	if not groups:
		return True
	else:	#Munge up the url to be correct
		url=mungeUrl(groups.group(0))
	try:
		info,title=getUrl(url)
	except Exception as e:
		bot.log(e,'warning')
		title='N/A'
	if len(title)>50: title=title[:47]+'...'
	try:
		if USE_RSS: sendToRSS(info,url,title,args[-1])
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
def INIT(bot):	#Config setup!
	global USE_RSS, RSS_FILEPATH, TINYURL, RSS_TITLE, RSS_LINK, RSS_MAX, MINSIZE
	if not bot.config.has_section('tinyurl'): return
	USE_RSS = bot.config.getboolean('tinyurl','userss')
	RSS_FILEPATH = os.path.abspath(bot.config.get('tinyurl','rssfilepath'))
	TINYURL = bot.config.get('tinyurl','tinyurl')
	RSS_TITLE = bot.config.get('tinyurl','rsstitle')
	RSS_LINK = bot.config.get('tinyurl','rsslink')
	RSS_MAX = bot.config.getint('tinyurl','rssmax')
	MINSIZE = bot.config.getint('tinyurl','mintitlesize')
def mungeUrl(url):
	if type(url)!=unicode:	#Convert unicode bytes to full chars
		url=unicode(url,'utf-8','replace')
	for i,c in enumerate(url):	#Iterate over the CHARs and clip on control chars
		if c < '\x09' or '\x0D'<c<'\x20' or c=='\x7F': break	#Found in mIRC formatting
	else: i=len(url)	#No clipping!
	url=url[:i]		#Clip
	spliturl=url.split('/')
	spliturl[2]=spliturl[2].encode('idna')	#convert domain to idna format
	if len(spliturl) > 3:	#clean up the path of unicode
		for i,s in enumerate(spliturl[3:]):
			spliturl[i+3]=urllib.quote(s.encode('utf-8'),'?&=')
	return '/'.join(spliturl)	#Join them back up!
def getUrl(url):
	"""Returns the (MIME, title) of a url where title is the <title>[content]</title> in html"""
	title, mime="N/A", 'application/octet-stream'
	socket.setdefaulttimeout(3)
	try:
		f=urllib.urlopen(url)
		mime = f.info().type
		length = f.info().get('Content-Length')
		if length == None: length=1	#Safe to assume that the minimum is always at least a byte
		if not mime.lower() == 'text/html': return (mime, length), title
		html=f.read(8096)	#Should grab most titles
		group=re.search(r'(?i)\<title\>(.*?)\<\/title\>',html, re.DOTALL)
		if not group: return (mime, length), title
		title=unicode(group.group(1),'utf-8', 'replace')
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
	return (mime, length), title
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
<ns0:link rel="self" xmlns:ns0="http://www.w3.org/2005/Atom" href="%s" type="application/rss+xml" />
</channel>
</rss>
""" % (RSS_TITLE,link,link)
	f=open(RSS_FILEPATH,'w')
	f.write(template)
	f.close()
def sendToRSS(info, url, title, poster):
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
			chan.insert(4,it)
			break
		elif i>RSS_MAX: r.append(it)
	else:
		for it in r: chan.remove(it)
		it=Element('item')
		SubElement(it,'title').text=title
		SubElement(it,'link').text=url
		SubElement(it,'pubDate').text=strftime(RSS_DATEFORMAT,localtime())
		SubElement(it,'guid').text=url
		if info[0] != 'text/html':
			enc=SubElement(it,'enclosure')
			enc.set('url',url)
			enc.set('type',info[0])
			enc.set('length',info[1])
		chan.insert(5,it)	#4 in order to bypass all the <title> and other tags
	f=codecs.open(RSS_FILEPATH,'w+','utf-8')
	f.write("""<?xml version="1.0" encoding="utf-8" ?>
<?xml-stylesheet type="text/css" title="CSS_formating" href="rss.css" ?>
<?xml-stylesheet type="text/xsl" href="rss.xsl" ?>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
""")
	e.write(f)
	f.close()
