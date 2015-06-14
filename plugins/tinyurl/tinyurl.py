from twisted.web.client import getPage
from plugin_lib import trigger
import json
import re

MINLEN=50
APIKEY=''

def parse_tinyurl(body, bot, channel):
  body = json.loads(body)
  tiny = body.get('id', '')
  bot.say(channel, 'Tiny: ' + tiny.encode('utf8'))

def parse_youtube(body, bot, channel, vid):
  body = json.loads(body)
  video_list = body.get(u'items',[])
  title = ''
  if len(video_list) > 0:
    title = video_list[0].get(u'snippet', {}).get(u'title', '').encode('utf8')
    if len(title) > 0: title += ' - '
  url = 'http://youtu.be/' + vid.encode('utf8')
  bot.say(channel, "Watch! (or don't, it probably sucks): %s%s" % (title, url))

@trigger('PRIVMSG', match=r'.*https?:\/\/\S+.*')
def tinyurl(bot, user, channel, msg):
  global MINLEN, APIKEY
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
    d = getPage("https://www.googleapis.com/youtube/v3/videos?key=%s&id=%s&part=snippet" % (APIKEY, vid))
    d.addCallback(parse_youtube, bot, channel, vid)
  elif len(url) < MINLEN:
    return
  else:
    d=getPage('https://www.googleapis.com/urlshortener/v1/url?key='+APIKEY, method='POST',
      postdata='{"longUrl": "%s"}' % url, headers={'Content-Type':'application/json'})
    d.addCallback(parse_tinyurl, bot, channel)
    d.addErrback(bot.log.err)

def init(bot):
  global MINLEN, APIKEY
  if bot.config.has_option('tinyurl', 'min_len'):
    MINLEN=bot.config.getint('tinyurl', 'min_len')
  if bot.config.has_option('tinyurl', 'api'):
    APIKEY=bot.config.get('tinyurl', 'api')
