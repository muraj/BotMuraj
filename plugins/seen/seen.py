
from plugin_lib import command, trigger
import datetime

seen_db = {}

@trigger('PRIVMSG')
def seen_track(bot, user, channel, msg):
  global seen_db
  seen_db[user] = datetime.utcnow()
  return True # Continue processing this message

@command('seen')
def seen_cmd(bot, user, channel, args):
  global seen_db
  for u in args:
    t = seen_db.get(u, None)
    if t == None:
      bot.say(channel, "I haven't seen %s" % (u))
    else:
      bot.say(channel, "I saw %s on %s" % (u, t.strftime('%X %Z %x')))
