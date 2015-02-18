
from plugin_lib import command

@command('reload')
def reload(bot, user, channel, args):
  """!reload <module> # Reloads the given module"""
  nick,_,hostmask = user.partition('!')
  if not bot.isOp(channel, nick):
    bot.say(channel, 'Op only, sorry')
    return

  if len(args) == 0: return

  msg = 'Failed to reload plugin '
  if bot.load_plugin(args[0], force=True):
    msg = 'Successfully reloaded plugin '

  bot.say(channel, msg + args[0])
