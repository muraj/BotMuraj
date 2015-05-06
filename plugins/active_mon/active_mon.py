from plugin_lib import command, trigger
import shelve
import os.path
from math import log
import hashlib
import mmap

active_db = None
#reducefn = len
cmd = 'souls'
bloomFilter = None

def hash_func(s, seed):
  # TODO: replace with something more efficient
  return int(hashlib.sha256(s + str(seed)).hexdigest(), base=16)

class BloomFilter(object):
  def __init__(self, n, p, filename, hash_f=hash_func):
    self._n, self._p = n, p
    self._m = int(- self._n * log(self._p) / log(2)**2 ) + 1
    self._k = int(log(2) * self._m / self._n) + 1
    self.hash_func = hash_f

    initialize_file = not os.path.exists(filename)

    if not initialize_file:
      self._file = open(filename, 'r+b')
    else: # Create the file
      self._file = open(filename, 'w+b')
      self._file.truncate((self._m+7) / 8)  # Set the file size
      self._file.flush()

    self._mmap = mmap.mmap(self._file.fileno(), (self._m+7) / 8, access=mmap.ACCESS_WRITE)

  def close(self):
    self._mmap.close()
    self._file.close()

  def setBit(self, i):
    idx, bit = i >> 3, i & 0x07
    self._mmap[idx] = chr(ord(self._mmap[idx]) | (1 << bit))
    #self._mmap.flush(idx,1)  # Sync memory and backing store

  def getBit(self, i):
    idx, bit = i >> 3, i & 0x07
    return ((ord(self._mmap[idx]) >> bit) & 1) == 1

  def _hashed_indices(self, s):
    for seed in range(self._k):
      h = self.hash_func(s, seed) % self._m
      yield h

  def add(self, s):
    for idx in self._hashed_indices(s):
      self.setBit(idx)

  def maybe_contains(self, s):
    for idx in self._hashed_indices(s):
      if not self.getBit(idx):
        return False
    return True

  def check_add(self, s):
    missing = False
    for idx in self._hashed_indices(s):
      if not self.getBit(idx):
        self.setBit(idx)
        missing = True
    return not missing

def reducefn(s):
  global bloomFilter
  return 0 if bloomFilter.check_add(s) else 1

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
  global active_db, reducefn, bloomFilter
  ACTIVE_DB_FILE = '~/.config/glitchbot/active.shelve'
  BLOOMFILTER_MMAP = '~/.config/glitchbot/active.bloom'
  if bot.config.has_option('active_mon', 'db'):
    ACTIVE_DB_FILE = bot.config.get('active_mon', 'db')

  active_db = shelve.open(os.path.expanduser(ACTIVE_DB_FILE))
  bloomFilter = active_db.get('__BLOOMFILTER__', None)
  if bloomFilter == None:
    # TODO: move to config file
    bloomFilter = [5000*365, 0.1, BLOOMFILTER_MMAP]

  active_db['__BLOOMFILTER__'] = bloomFilter
  active_db.sync()

  bloomFilter[-1] = os.path.expanduser(bloomFilter[-1])
  bloomFilter = BloomFilter(*bloomFilter)
