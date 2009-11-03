"""Pulls information off a woot subsite's rss, providing the price, product, percent to sellout, and link to buy"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, xml.etree.ElementTree, re
RULE=r'^(([A-Za-z0-9]+\.)?woot).*'
PRIORITY=10
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
DOTINYURL=True
TINYURL='http://tinyurl.com/api-create.php?'
def PROCESS(bot, args, text):
	woot=re.search(r'^(([A-Za-z0-9]+\.)?woot).*',text).group(1)
	f=urllib.urlopen('http://%s.com/salerss.aspx' % (woot))
	e=xml.etree.ElementTree.parse(f)
	price=e.findtext('/channel/item/{http://www.woot.com/}price')
	product=e.findtext('/channel/item/{http://www.woot.com/}products/{http://www.woot.com/}product')
	if len(product)>50: product=product[:47]+'...'
	percent=e.findtext('/channel/item/{http://www.woot.com/}soldout')
	wootoff=e.findtext('/channel/item/{http://www.woot.com/}wootoff')
	wootoff = 'I want one!' if wootoff=='False' else 'WootOff!'
	url=e.findtext('/channel/item/{http://www.woot.com/}purchaseurl')
	if percent == 'False':
		percent=100*float(e.findtext('channel/item/{http://www.woot.com/}soldoutpercentage'))
		percent="%.2f%%" % (percent)
		if TINYURL: url=getTiny(url)
	else:
		url="http://%s.com" % woot
	bot.mesg(u"%s \"%s\" %s: %s %s" % (price, product, percent, wootoff, url), args[1])
	f.close()
	return False
def INIT(bot):
	global DOTINYURL, TINYURL
	if not bot.config.has_section('woot'): return
	DOTINYURL = bot.config.getboolean('woot','usetinyurl')
	TINYURL = bot.config.get('woot','tinyurl') if DOTINYURL else None
def getTiny(url):
	"""Returns the TinyURL version of <url>"""
	TINYURL,tinyurl='http://tinyurl.com/api-create.php?','N/A'
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
