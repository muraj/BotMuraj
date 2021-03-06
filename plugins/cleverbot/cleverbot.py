from plugin_lib import trigger
from twisted.web.client import getPage
from collections import OrderedDict
import urllib
import hashlib
import re
from HTMLParser import HTMLParser

service_url = 'http://www.cleverbot.com/webservicemin'

post_params = OrderedDict(
  [('start','y'),
  ('icognoid','wsf'),
  ('fno','0'),
  ('sub','Say'),
  ('islearning','1'),
  ('cleanslate','false')]
)

sessions = {}

def parse_body(body, bot, user, channel):
  global post_params, sessions
  vals = body.split('\r')
  if len(vals) < 24:
    bot.log.err('Returned list is too small')
    return
  params, cookiejar = sessions.get(channel, [post_params, {}])
  params['sessionid'] = vals[1]
  params['logurl'] = vals[2]
  params['vText8'] = vals[3]
  params['vText7'] = vals[4]
  params['vText6'] = vals[5]
  params['vText5'] = vals[6]
  params['vText4'] = vals[7]
  params['vText3'] = vals[8]
  params['vText2'] = vals[9]
  params['emotionalhistory'] = vals[12]
  params['ttsLocMP3'] = vals[13]
  params['ttsLocTXT'] = vals[14]
  params['ttsLocTXT3'] = vals[15]
  params['ttsText'] = vals[16]
  params['lineRef'] = vals[17]
  params['lineURL'] = vals[18]
  params['linePOST'] = vals[19]
  params['lineChoices'] = vals[20]
  params['lineChoicesAbbrev'] = vals[21]
  params['typingData'] = vals[22]
  params['divert'] = vals[23]
  sessions[channel] = [params, cookiejar]
  user, _, _ = user.partition('!')
  # Parse out the html with proper unicode characters
  resp = vals[16] = HTMLParser().unescape(vals[16]).encode('utf8')
  resp = re.sub(r'\|([A-Za-z0-9]{1,4})', lambda x: unichr(int(x.group(1), 16)), resp)
  resp = resp.encode('utf8')
  bot.log.msg("cleverbot got response: '%s'" % resp)
  # Many actions end with '*.', but some end with '*'
  if resp.startswith('*') and (resp[-2:] == '*.' or resp[-1] == '*'):
    # send a ctcp action instead
    bot.me(channel, resp[1:(-1 if resp[-1] == '*' else -2)])
  else:
    bot.msg(channel, "%s: %s" % (user, resp))

def cleverbot_respond(bot, user, channel, msg):
  global service_url, post_params, sessions
  msg = re.sub(bot.nickname, 'cleverbot', msg)
  bot.log.msg("Sending response: '%s'" % msg)
  encodedmsg = ''
  for c in msg.decode('utf8', errors='replace'):
    encodedmsg += c if ord(c) < 128 else u'|%04X'%ord(c)
  msg = encodedmsg
  bot.log.msg("Sending encoded response: '%s'" % msg)
  params, cookiejar = sessions.get(channel, [post_params, {}])
  sessions[channel] = [params, cookiejar]
  if not cookiejar: # Get initial session cookie
    d = getPage('http://www.cleverbot.com/', cookies=cookiejar)
    d.addCallback(lambda _: cleverbot_respond(bot, user, channel, msg))
    return
  params['stimulus'] = msg
  params['icognocheck'] = hashlib.md5(urllib.urlencode(params)[9:35]).hexdigest()
  d = getPage(service_url, method='POST', postdata=urllib.urlencode(params),
      timeout=20, cookies=cookiejar)
  d.addCallback(parse_body, bot, user, channel)
  d.addErrback(bot.log.err)

@trigger('ACTION', priority=9999)
def cleverbot_action_trigger(bot, user, channel, msg):
  # Convert the ctcp action to cleverbot format
  msg = '*'+msg+'*'
  return cleverbot_respond(bot, user, channel, msg)

@trigger('PRIVMSG', priority=9999)
def cleverbot_trigger(bot, user, channel, msg):
  if not user.startswith(channel):
    if not msg.startswith(bot.nickname):
      return
  if msg.startswith(bot.nickname):
    msg = re.sub(bot.nickname + '\\S+', '', msg).strip()
  return cleverbot_respond(bot, user, channel, msg)
