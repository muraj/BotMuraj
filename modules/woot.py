"""Pulls information off a woot subsites' rss, providing the price, product, percent to sellout, and link to product"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, xml.etree.ElementTree, re
RULE=r'^(([A-Za-z0-9]+\.)?woot).*'
PRIORITY=10
COMMAND='PRIVMSG'
DIRECTED=1	#Must be directed to the bot
def PROCESS(bot, args, text):
	woot=re.search(r'^(([A-Za-z0-9]+\.)?woot).*',text).group(1)
	f=urllib.urlopen('http://%s.com/salerss.aspx' % (woot))
	e=xml.etree.ElementTree.parse(f)
	price=e.findtext('/channel/item/{http://www.woot.com/}price')
	condition=e.findtext('/channel/item/{http://www.woot.com/}condition')
	product=e.findtext('/channel/item/title')
	if condition.lower() != 'new': product=condition+' '+product
	percent=e.findtext('/channel/item/{http://www.woot.com/}soldout')
	wootoff=e.findtext('/channel/item/{http://www.woot.com/}wootoff')
	wootoff='' if wootoff=='False' else '\x02\x0301,08WootOff!\x0F '
	if percent == 'False':
		percent=100*float(e.findtext('channel/item/{http://www.woot.com/}soldoutpercentage'))
		percent="%.2f%% sold" % (percent)
	else: percent='\x0300,05SOLD OUT\x0F'
	url="http://%s.com/" % woot
	bot.mesg(u"%s \x02%s\x0F %s: %s%s" % (price, product, percent, wootoff, url), args[1])
	f.close()
	return False
