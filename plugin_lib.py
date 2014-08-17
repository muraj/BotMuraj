import shlex
import re

class Trigger(object):
  def __init__(self, cmd, callback, user='*!*@*', channel='*', txt_match='.*', priority=999):
    self.callback = callback
    self.__doc__ = callback.__doc__
    self.cmd = cmd
    self.user = re.compile(user.replace('*', '[^!@]*'))
    self.channel = re.compile(channel.replace('*', '\\w*'))
    self.txt = re.compile(txt_match)
    self.priority = priority

  def match(self, bot, cmd, user, channel, msg):
    if cmd != self.cmd:
      return False
    if not self.channel.match(channel):
      return False
    if not self.user.match(user):
      return False
    if not self.txt.match(msg):
      return False
    return True

  def __call__(self, bot, cmd, user, channel, msg):
    if not self.match(bot, cmd, user, channel, msg):
      return True
    return self.callback(bot, user, channel, msg)

  def __lt__(self, other):
    return self.priority < other.priority
  def __le__(self, other):
    return self.priority <= other.priority
  def __gt__(self, other):
    return self.priority > other.priority
  def __ge__(self, other):
    return self.priority >= other.priority
  def __eq__(self, other):
    return self.priority == other.priority
  def __ne__(self, other):
    return self.priority != other.priority


class Command(Trigger):
  def __init__(self, name, callback, user='*!*@*', channel='*', priority=999):
    self.name = name
    def cb_wrapper(bot, user, channel, msg):
      return callback(bot, user, channel, shlex.split(msg)[1:])
    cb_wrapper.__doc__ = callback.__doc__
    Trigger.__init__(self, 'PRIVMSG', cb_wrapper, user, channel, '!' + name, priority=priority)

def trigger(cmd, user='*!*@*', channel='*', match='.*', priority=999):
  def decorator(func):
    return Trigger(cmd, func, user, channel, match)
  return decorator

def command(name, user='*!*@*', channel='*', priority=999):
  def decorator(func):
    return Command(name, func, user, channel)
  return decorator
