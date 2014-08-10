import time
from plugin_lib import command

START_TIME = time.time()
SCALE = 80.0 / 31556926.0

def uptime(bot, user, channel, args, penis=False):
  t = time.time() - START_TIME
  minutes = int(t / 60)
  seconds = t - minutes * 60
  bot.say(channel, "I've been up for %d minutes and %d seconds" % (minutes, seconds))
  if penis:
    shaft_len = int(t * SCALE)
    bot.say(channel, '\x03138=' + ('=' * shaft_len) + 'D')

@command('uptime')
def cmd_uptime(bot, user, channel, args):
  """!uptime # What's the current uptime of the bot?"""
  return uptime(bot, user, channel, args)

@command('penis')
def penis(bot, user, channel, args):
  """!penis # How big is yours?"""
  return uptime(bot, user, channel, args, True)
