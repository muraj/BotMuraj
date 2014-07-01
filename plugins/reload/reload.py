
from plugin_lib import command

@command('reload')
def reload(bot, user, channel, args):
  """!reload <module> # Reloads the given module"""
  if not bot.isOp(channel, user):
    bot.say(channel, 'Op only, sorry')
    return
  if len(args) == 0: return
  bot.reload(args[0])
