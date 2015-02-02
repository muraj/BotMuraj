from twisted.web.client import getPage
from plugin_lib import trigger
import xml.etree.ElementTree
import json
import re

MINLEN=50

def parse_tinyurl(body, bot, channel):
  body = json.loads(body)
  tiny = body.get('id', None)
  bot.say(channel, 'Tiny: ' + tiny.encode('utf8'))

def parse_youtube(body, bot, channel, vid):
  e = xml.etree.ElementTree.fromstring(body)
  title = e.findtext('{http://www.w3.org/2005/Atom}title').encode('utf8')
  url = 'http://youtu.be/' + vid.encode('utf8')
  bot.say(channel, "Watch! (or don't, it probably sucks): %s - %s" % (title, url))

@trigger('PRIVMSG', match=r'.*https?:\/\/\S+.*')
def tinyurl(bot, user, channel, msg):
  global MINLEN
  groups = re.search(r'https?:\/\/([^\/\s]+)\S*', msg)
  if not groups: return
  url = groups.group(0)
  host = groups.group(1)
  # Remove www from host if it exists...
  host = host[4:] if host.startswith('www.') else host
  bot.log.msg('Got url ' + url)
  youtube_groups = None
  if host == 'youtube.com':
    youtube_groups = re.search(r'\bv=([^&]+)', url)
  else:
    youtube_groups = re.search(r'be\/([^?]+)', url)
  if youtube_groups:
    vid = youtube_groups.group(1)
    d = getPage("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % vid)
    d.addCallback(parse_youtube, bot, channel, vid)
  elif len(url) < MINLEN:
    return
  else:
    d=getPage('https://www.googleapis.com/urlshortener/v1/url', method='POST',
      postdata='{"longUrl": "%s"}' % url, headers={'Content-Type':'application/json'})
    d.addCallback(parse_tinyurl, bot, channel)
    d.addErrback(bot.log.err)

def init(bot):
  global MINLEN
  if bot.config.has_option('tinyurl', 'min_len'):
    MINLEN=bot.config.getint('tinyurl', 'min_len')
