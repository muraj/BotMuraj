from plugin_lib import command, trigger
import time

seen_db = {}

@trigger('PRIVMSG', priority=10)
def seen_track(bot, user, channel, msg):
  global seen_db
  user, _, _ = user.partition('!')
  seen_db[user] = time.time()
  bot.log.msg("Saw %s at %s" % (user, time.ctime(seen_db[user])))
  return True # Continue processing this message

@command('seen')
def seen_cmd(bot, user, channel, args):
  global seen_db
  for u in args:
    t = seen_db.get(u, None)
    if t == None:
      bot.say(channel, "I haven't seen %s" % (u))
    else:
      localtime = time.localtime(t)
      bot.say(channel, "I saw %s on %s" % (u, time.strftime("%X %Z %x", localtime)))
