from twisted.web.client import getPage
from plugin_lib import command
import xml.etree.ElementTree

def parse_body(body, bot, url, channel):
  e = xml.etree.ElementTree.fromstring(body)
  price = e.findtext('channel/item/{http://www.woot.com/}price')
  condition = e.findtext('channel/item/{http://www.woot.com/}condition')
  product = e.findtext('channel/item/title')
  if condition.lower() != 'new': 
    product = condition +' '+product
  percent=e.findtext('channel/item/{http://www.woot.com/}soldout')
  wootoff=e.findtext('channel/item/{http://www.woot.com/}wootoff')
  wootoff='' if wootoff.lower()=='false' else '\x02\x0301,08WootOff!\x0F '
  if percent.lower() == 'false':
    percent=100*float(e.findtext('channel/item/{http://www.woot.com/}soldoutpercentage'))
    percent="%.2f%% sold" % (percent)
  else: percent='\x0300,05SOLD OUT\x0F'
  bot.say(channel, "%s \x02%s\x0F %s: %shttp://%s.com/" % (price, product, percent, wootoff, url))

@command('woot')
def cmd_woot(bot, user, channel, args):
  """!woot [<sub>] # Returns the current woot sale for the current sub woot site"""
  base_url = 'woot'
  if len(args) != 0:
    base_url = args[0] + '.' + base_url
  url = "http://%s.com/salerss.aspx" % (base_url)
  d = getPage(url, timeout=10)
  d.addCallback(parse_body, bot, base_url, channel)
  d.addErrback(bot.log.err)
