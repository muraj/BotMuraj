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

def parse_youtube(body, bot, channel):
  e = xml.etree.ElementTree.fromstring(body)
  title = e.findtext('title')
  bot.say(channel, title)

@trigger('PRIVMSG', match=r'.*https?:\/\/\S+.*')
def tinyurl(bot, user, channel, msg):
  global MINLEN
  groups = re.search(r'https?:\/\/([^\/\s]+)\S*', msg)
  if not groups: return
  url = groups.group(0)
  host = groups.group(1)
  # Remove www from host if it exists...
  host = host[4:] if host.startswith('www.') else host
  #if host == 'youtube.com' or host == 'youtu.be':
  #  youtube_groups = re.search(r'\bv=([^&]+)', url)
  #  if youtube_groups:
  #    vid = youtube_groups.group(0)
  #    d = getPage("https://gdata.youtube.com/feeds/api/videos/%s?v=2" % vid)
  #    # Do something with d here
  if len(url) < MINLEN: return
  d=getPage('https://www.googleapis.com/urlshortener/v1/url', method='POST',
    postdata='{"longUrl": "%s"}' % url, headers={'Content-Type':'application/json'})
  d.addCallback(parse_tinyurl, bot, channel)
  d.addErrback(bot.log.err)

def init(bot):
  global MINLEN
  if bot.config.has_option('tinyurl', 'min_len'):
    MINLEN=bot.config.getint('tinyurl', 'min_len')
