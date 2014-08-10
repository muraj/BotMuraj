
from plugin_lib import command, Command

@command('help')
def cmd_help(bot, user, channel, args):
  if len(args) == 0:
    cmds = []
    for fn in bot.iterTriggers():
      if isinstance(fn, Command):
        cmds.append(fn.name)
    bot.say(channel, "Available commands: %s.  For more, say '!help CMD'." % ', '.join(cmds))
  else:
    for fn in bot.iterTriggers():
      if isinstance(fn, Command) and fn.name == args[0]:
        doc = fn.__doc__ if fn.__doc__ else 'No help available'
        bot.say(channel, fn.name + ': ' + doc)
        break
