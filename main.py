#!/usr/bin/python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from twisted.python import log
import ConfigParser
import os.path
import glob
import imp
import sys
import heapq

from plugin_lib import Trigger

class GlitchBot(irc.IRCClient):

  def __init__(self, config, reactor):
    self.config = config
    self.reactor = reactor
    self.pluginDir = os.path.dirname(os.path.realpath(__file__)) + '/plugins'
    self.channels = {}
    self.modules = []
    self.sentMessages = 0
    self._namesCallbacks = {}
    self.log = log

    self.username = config.get('Bot', 'username')
    if config.has_option('Bot', 'password'):
      self.password = config.get('Bot', 'password')
    if config.has_option('Bot', 'pluginPath'):
      self.pluginDir = config.get('Bot', 'pluginPath')
    if config.has_option('Bot', 'nick'):
      self.nickname = config.get('Bot', 'nick')
    # Add local directory to path for plugins to use plugin_lib for Trigger
    sys.path.append(os.path.realpath(__file__))
    self.load_plugins()

  def load_plugins(self):
    log.msg('Loading plugins...')
    self.modules = []
    for plugin in glob.glob(self.pluginDir + '/*/'):
      key = os.path.basename(os.path.dirname(plugin))
      try:
        if not self.config.getboolean(key, 'enable'):
          continue
        log.msg("Loading %s plugin..." % key)
        f, p, desc = imp.find_module(key, [plugin])
        module = imp.load_module(key, f, p, desc)
        if hasattr(module, 'init') and callable(module.init):
          module.init(self)
        self.modules.append(module)
      except:
        log.err()

  def iterTriggers(self):
    h = []
    for m in self.modules:    # Not the most efficient way to do this...
      for name, fn in vars(m).iteritems():
        if isinstance(fn, Trigger):
          heapq.heappush(h, fn)
    while len(h) != 0:
      yield heapq.heappop(h)

  def reload_plugin(self, name):
    log.msg("Reloading %s plugin" % name)
    for i,m in enumerate(self.modules):
      if name == m.__name__:
        try:
          m = imp.reload(m)
          if hasattr(m, 'init') and callable(m.init):
            m.init(self)
          log.msg("Reloaded %s plugin" % name)
          self.modules[i] = m
        except:
          log.err()

  def signedOn(self):
    if not self.config.has_option('Bot', 'chans'): return
    for c in self.config.get('Bot', 'chans').strip('"').split(' '):
      if c: self.join(c)

  def userMode(self, channel, nick):
    nicklist = self.channels.get(channel, {})
    return next(( v[1] for v in nicklist.itervalues() if v[0] == nick), None)
    
  def isOp(self, channel, nick):
    nicklist = self.channels.get(channel, {})
    mode = self.userMode(channel, nick)
    return ('@' in mode) if mode else False

  def isAdmin(self, channel, nick):
    nicklist = self.channels.get(channel, {})
    mode = self.userMode(channel, nick)
    return ('*' in mode) if mode else False

  def hasVoice(self, channel, nick):
    nicklist = self.channels.get(channel, {})
    mode = self.userMode(channel, nick)
    return ('+' in mode) if mode else False

  def __setNames(self, nickDict, channel):
    self.channels[channel] = nickDict

  def refreshIAL(self, channel):
    log.msg('Refreshing IAL for channel ' + channel)
    channel = channel.lower()
    d = defer.Deferred()
    self.sendLine('WHO ' + channel)
    li = self._namesCallbacks.get(channel, ([],{}))
    li[0].append(d)
    self._namesCallbacks[channel] = li
    d.addCallback(self.__setNames, channel)
    return d

  def irc_RPL_WHOREPLY(self, prefix, params):
    channel = params[1].lower()
    nick, user, host, mode = params[5], params[2], params[3], params[6]
    if not channel in self._namesCallbacks: return
    self._namesCallbacks[channel][1][user + '@' + host] = [ nick, mode ]

  def irc_RPL_ENDOFWHO(self, prefix, params):
    channel = params[1].lower()
    if not channel in self._namesCallbacks: return
    nickDict = self._namesCallbacks[channel][1]
    for cb in self._namesCallbacks[channel][0]:
      cb.callback(nickDict)
    del self._namesCallbacks[channel]

  def joined(self, channel):
    log.msg('Joined channel: ' + channel)
    self.channels[channel] = {}
    self.refreshIAL(channel)

  def modeChanged(self, user, channel, set, modes, args):
    if channel in self.channels:
      self.refreshIAL(channel)   # HACK! Make this more efficient please!
    return irc.IRCClient.modeChanged(self, user, channel, set, modes, args)

  def irc_NICK(self, prefix, params):
    for chan in self.channels.iterkeys():
      self.refreshIAL(channel)  # HACK! Make this more efficient please!

  def irc_PART(self, prefix, params):
    channel = params[0]
    if channel in self.channels:
      self.refreshIAL(channel)  # HACK! Make this more efficient please!

  def left(self, channel):
    log.msg('Left channel: ' + channel)
    del self.channels[channel]  # Delete all info about this channel

  def privmsg(self, user, channel, msg):
    if channel == self.nickname:
      channel, _, _ = user.partition('!')
    for fn in self.iterTriggers():
      try:
        if not fn(self, 'PRIVMSG', user, channel, msg):
          break
      except:
        log.err()

class GlitchBotFactory(protocol.ClientFactory):
  def __init__(self, config, reactor):
    self.config = config
    self.reactor = reactor

  def buildProtocol(self, addr):
    bot = GlitchBot(self.config, self.reactor)
    bot.factory = self
    return bot

  def clientConnectionLost(self, connector, reason):
    connector.connect()

  def clientConnectionFailed(self, connector, reason):
    reactor.stop()

if __name__ == '__main__':
  config = ConfigParser.ConfigParser()
  defaultCfg = os.path.expanduser('~/.config/glitchbot')
  if not os.path.exists(defaultCfg):
    os.mkdir(defaultCfg)
  config.read(['default.cfg', defaultCfg + '/config.cfg'])
  host = config.get('Bot', 'host')
  port = 6667
  if config.has_option('Bot', 'port'):
    port = config.getint('Bot', 'port')
  fact = GlitchBotFactory(config, reactor)
  reactor.connectTCP(host, port, fact)
  log.startLogging(sys.stdout)
  reactor.run()
