"""Pulls information off a woot subsites' rss, providing the price, product, percent to sellout, and link to product"""
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
	wootoff='' if wootoff=='False' else 'WootOff! '
	if percent == 'False':
		percent=100*float(e.findtext('channel/item/{http://www.woot.com/}soldoutpercentage'))
		percent="%.2f%%" % (percent)
	else: percent='SOLD OUT'
	url="http://%s.com/" % woot
	bot.mesg(u"%s \"%s\" %s sold: %s%s" % (price, product, percent, wootoff, url), args[1])
	f.close()
	return False
