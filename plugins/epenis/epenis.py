import time
from plugin_lib import command

START_TIME = time.time()
SCALE = 80.0 / 31556926.0

def uptime(bot, user, channel, args, penis=False):
  t = time.time() - START_TIME
  shaft_len = int(t * SCALE)
  days, t = divmod(t, 24*3600)
  hours, t = divmod(t, 3600)
  minutes, seconds = divmod(t, 60)
  days = '' if days == 0 else "%d days " % days
  hours = '' if hours == 0 else "%d hours " % hours
  minutes = '' if minutes == 0 else "%d minutes " % minutes
  seconds = '' if seconds == 0 else "%d seconds " % seconds
  bot.say(channel, "I've been up for %s%s%s%s" % (days, hours, minutes, seconds))
  if penis:
    bot.say(channel, '\x03138=' + ('=' * shaft_len) + 'D')

@command('uptime')
def cmd_uptime(bot, user, channel, args):
  """!uptime # What's the current uptime of the bot?"""
  return uptime(bot, user, channel, args)

@command('penis')
def penis(bot, user, channel, args):
  """!penis # How big is yours?"""
  return uptime(bot, user, channel, args, True)
