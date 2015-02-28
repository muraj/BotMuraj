from twisted.web.client import Agent
from twisted.internet import reactor
from plugin_lib import command
import random

SUBREDDITS=['']

def bored_resp(resp, bot, user, channel):
  global URL_PARSER
  url=''.join(resp.headers.getRawHeaders('location'))
  url=url[url.rindex('/'):]
  bot.msg(channel, 'Check this out: http://reddit.com' + url)

@command('bored')
def bored_cmd(bot, user, channel, args):
  global SUBREDDITS
  url = random.choice(SUBREDDITS)
  if len(url) != 0: url += '/'
  url = 'http://www.reddit.com/' + url + 'random'
  bot.log.msg('Requesting ' + url)
  d = Agent(reactor).request('GET', url)
  d.addCallback(bored_resp, bot, user, channel)

def init(bot):
  global SUBREDDITS
  if bot.config.has_option('reddit', 'subreddits'):
    SUBREDDITS+=bot.config.get('reddit', 'subreddits').split(',')
