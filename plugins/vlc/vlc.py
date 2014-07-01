from plugin_lib import command
from xml.etree import ElementTree
from twisted.web.client import getPage
import urllib
import base64

SERVER_URL=''
SERVER_AUTH=''
SERVER_STREAM=''

def init(bot):
  global SERVER_URL, SERVER_STREAM, SERVER_AUTH
  SERVER_URL = 'http://' + bot.config.get('vlc', 'host')
  SERVER_STREAM = bot.config.get('vlc', 'stream')
  user = ''
  passwd = bot.config.get('vlc', 'password')
  SERVER_AUTH = 'Basic ' + base64.encodestring(user + ':' + passwd).strip()

def getAuthedPage(url, bot):
  d=getPage(url, headers={'Authorization':SERVER_AUTH})
  d.addErrback(bot.log.err)
  return d

def handle_status(body, bot, channel):
  e = ElementTree.fromstring(body)
  metaNode = e.find("information/category[@name='meta']")
  if metaNode is None: return # In case of errors
  title = metaNode.findtext("info[@name='title']")
  artist = metaNode.findtext("info[@name='artist']")
  if not artist:  # For sound cloud, only title and url are available
    artist = metaNode.findtext("info[@name='url']", '')
  msg = "Currently playing: '%s', %s" % (title, artist)
  bot.say(channel, msg)

def cmd_status(bot, user, channel, args):
  d = getAuthedPage(SERVER_URL + '/requests/status.xml', bot)
  d.addCallback(handle_status, bot, channel)
  return d

def cmd_add(bot, user, channel, args):
  if not bot.isOp(channel, user):
    bot.say(channel, 'Op only, sorry')
    return
  if len(args) == 0: return
  if not args[0].startswith('http://'): return
  quoted = urllib.quote(args[0])
  return getAuthedPage(SERVER_URL + '/requests/status.xml?command=in_enqueue&input=' + quoted, bot)

def cmd_play(bot, user, channel, args):
  if not bot.isOp(channel, user):
    bot.say(channel, 'Op only, sorry')
    return
  if len(args) == 0: return
  if not args[0].startswith('http://'): return
  quoted = urllib.quote(args[0])
  return getAuthedPage(SERVER_URL + '/requests/status.xml?command=in_play&input=' + quoted, bot)

def cmd_skip(bot, user, channel, args):
  if not bot.isOp(channel, user):
    bot.say(channel, 'Op only, sorry')
    return
  return getAuthedPage(SERVER_URL + '/requests/status.xml?command=pl_next', bot)

@command('vlc')
def vlc(bot, user, channel, args):
  """!vlc [status|add|play|skip] [<URL>] # Controls a vlc http interface.  \
URL can be any http url that vlc can stream (sondcloud, youtube)"""
  if len(args) == 0:
    bot.say(channel, 'Listen to music at: ' + SERVER_STREAM)
    return
  bot.log.msg("Calling %s subcommand" % args[0])
  cmd = globals().get('cmd_' + args[0], lambda b,u,c,a: None)
  cmd(bot, user, channel, args[1:])
