from plugin_lib import command, Command
from twisted.web.client import getPage
import urllib
import hashlib

service_url = 'http://www.cleverbot.com/webservicemin'
post_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'en-us;q=0.8,en;q=0.5',
           'X-Moz': 'prefetch',
           'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
           'Referer':'http://www.cleverbot.com',
           'Cache-Control':'no-cache, no-cache',
           'Pragma':'no-cache'}

post_params = {
  'start':'y',
  'icognoid':'wsf',
  'fno':'0',
  'sub':'Say',
  'islearning':'1',
  'cleanslate':'false'
}

def parse_body(body, bot, user, channel):
  pass

@trigger('PRIVMSG')
def cleverbot_trigger(bot, user, channel, msg):
  global service_url, post_headers, post_params
  params = post_params
  params['stimulus'] = msg
  params['icognocheck'] = hashlib.md5(urllib.urlencode(params)).hexdigest()
  d = getPage(service_url, method='POST', postdata=urllib.urlencode(params),
      headers=post_headers, timeout=10)
  d.addCallback(parse_body, bot, user, channel)
  d.addErrback(bot.log.err)
