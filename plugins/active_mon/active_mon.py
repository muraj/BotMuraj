from plugin_lib import command, trigger
import shelve

active_db = None
reducefn = len
cmd = 'souls'

@trigger('PRIVMSG')
def activity_track(bot, user, channel, msg):
  global active_db, reducefn
  user, _, _ = user.partition('!')
  active_db[user.lower()] = reducefn(msg)
  active_db.sync()
  return True # Continue processing this message

@command(cmd)
def activity(bot, user, channel, args):
  global active_db, cmd
  if len(args) == 0:
    args = [user.partition('!')[0]]
  for u in args:
    v = active_db.get(u.lower(), 0)
    bot.say(channel, "%s has %s %s" % (u, str(v), cmd))

@command('top_'+cmd)
def top_active(bot, user, channel, args):
  global active_db, cmd
  top = sorted(active_db.items(), key=lambda t: t[1], reverse=True)[0]
  bot.say(channel, "%s has the most %s with %s", top[0], cmd, str(top[1]))

def init(bot):
  global active_db, reducefn
  ACTIVE_DB_FILE = '~/.config/glichbot/active.shelve'
  if bot.config.has_option('active_mon', 'db'):
    ACTIVE_DB_FILE = bot.config.get('active_mon', 'db')
  active_db = shelve.open(os.path.expanduser(ACTIVE_DB_FILE))
