
from plugin_lib import command

@command('join')
def join(bot, user, channel, args):
  """!join <chan1> <chan2> # Tells the bot to join the given channels"""
  for c in args:
    bot.join(c)

@command('leave')
def leave(bot, user, channel, args):
  """!leave <chan1> <chan2> # Tells the bot to leave the given channels"""
  for c in args:
    bot.leave(c)
