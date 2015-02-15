from plugin_lib import command, trigger
import shelve
import os.path

active_db = None
reducefn = len
cmd = 'souls'

@trigger('PRIVMSG')
def activity_track(bot, user, channel, msg):
  global active_db, reducefn
  user, _, _ = user.partition('!')
  user_chan = user.lower() + '!' + channel
  active_db[user_chan] = active_db.get(user_chan, 0) + reducefn(msg.decode('utf-8'))
  active_db.sync()
  return True # Continue processing this message

@command(cmd)
def activity(bot, user, channel, args):
  """Prints out the current activity score for the requester if a \
  user isn't given server of bot"""
  global active_db, cmd
  if len(args) == 0:
    args = [user.partition('!')[0]]
  for u in args:
    user_chan = u.lower() + '!' + channel
    v = active_db.get(user_chan, 0)
    bot.say(channel, "%s has %s %s" % (u, str(v), cmd))

@command('top_'+cmd)
def top_active(bot, user, channel, args):
  """Prints out the current activity score for the user with the highest score."""
  global active_db, cmd
  top = sorted(active_db.items(), key=lambda t: t[1], reverse=True)[0]
  user, score = top[0].partition('!')[0], top[1]
  bot.say(channel, "%s has the most %s with %s" % (user, cmd, str(score)))

def init(bot):
  global active_db, reducefn
  ACTIVE_DB_FILE = '~/.config/glitchbot/active.shelve'
  if bot.config.has_option('active_mon', 'db'):
    ACTIVE_DB_FILE = bot.config.get('active_mon', 'db')
  active_db = shelve.open(os.path.expanduser(ACTIVE_DB_FILE))
