from plugin_lib import command, trigger
import time
import shelve
import os.path

seen_db = None
TIME_FORMAT='%X %Z %x'

@trigger('PRIVMSG', priority=10)
def seen_track(bot, user, channel, msg):
  global seen_db
  user, _, _ = user.partition('!')
  seen_db[user.lower()] = time.time()
  seen_db.sync()  # Sync as soon as possible in case of issues
  #bot.log.msg("Saw %s at %s" % (user, time.ctime(seen_db[user])))
  return True # Continue processing this message

@command('seen')
def seen_cmd(bot, user, channel, args):
  global seen_db, TIME_FORMAT
  for u in args:
    t = seen_db.get(u.lower(), None)
    if t == None:
      bot.say(channel, "I haven't seen %s" % (u))
    else:
      localtime = time.localtime(t)
      bot.say(channel, "I saw %s on %s" % (u, time.strftime(TIME_FORMAT, localtime)))

def init(bot):
  global TIME_FORMAT, seen_db
  if bot.config.has_option('seen', 'time_format'):
    TIME_FORMAT = bot.config.get('seen', 'time_format', raw=True)
  SEEN_DB_FILE = '~/.config/glitchbot/seen.shelve'
  if bot.config.has_option('seen', 'db'):
    SEEN_DB_FILE = bot.config.get('seen', 'db')
  seen_db = shelve.open(os.path.expanduser(SEEN_DB_FILE))
