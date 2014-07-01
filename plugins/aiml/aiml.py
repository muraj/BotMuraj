from plugin_lib import trigger
import .aiml.kernel

aimlkernel = aiml.Kernel()

@trigger('PRIVMSG')
def aiml(bot, user, channel, msg):
  """Hold a conversation with the bot.  Either start your messages with his \
nick, or query him to start"""
  global aimlkernel
  if not (channel.startswith(bot.nick) or msg.startswith(bot.nick)):
    return  # Isn't directed at the bot
  if msg.startswith(bot.nick):
    msg = msg[len(bot.nick)+1:]  # cut off the directed part if it exists
  nick, userid = user.split('!')
  aimlkernel.setPredicate('name', nick, userid)
  resp = aimlkernel.respond(msg, userid)
  if not channel.startswith(bot.nick):
    resp = nick + ': ' + resp
  bot.say(channel, resp)

def init(bot):
  global aimlkernel
  aimlkernel.verbose(True)
  bot.log.msg('Performing brain surgery...')
  aimlkernel.loadBrain(config.get('aiml', 'brain'))
  bot.log.msg('Operation success!')
  master_nick = config.get('aiml', 'master')
  aimlkernel.setBotPredicate('name', bot.nick)
  bot.log.msg('Teaching bot the meaning of life...')
  for var, val in config.items('aiml.vars'):
    aimlkernel.setBotPredicate(var, str(val))
  bot.log.msg('Operation success!')
