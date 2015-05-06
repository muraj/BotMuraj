#!/usr/bin/python2

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
    self.modules = {}
    self.sentMessages = 0
    self._namesCallbacks = {}
    self._signedOnCallbacks = []
    self.log = log

    # backwards compat for sending ctcp actions
    if getattr(self, 'me', None) == None:
      self.me = lambda c,a: self.describe(c,a)

    import time
    self.start_time = time.time()

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

  def load_plugin(self, name, force=False, load_deps=True):
    log.msg("Loading %s plugin..." % name)
    if not self.config.getboolean(name, 'enable'):
      return False

    module = self.modules.get(name, None)
    if module != None and not force:
      return True   # Already loaded plugin

    try:    # Load the module with the plugin
      f, p, desc = imp.find_module(name, [os.path.join(self.pluginDir, name)])
      with f: module = imp.load_module(name, f, p, desc)
    except:
      log.err()
      return False

    if load_deps:
      for dep in getattr(module, 'dependencies', []):
        self.load_plugin(dep, force, load_deps)

    try:
      getattr(module, 'init', lambda b: None)(self)
    except:
      log.err()
      return False

    self.modules[name] = module
    return True

  def load_plugins(self):
    log.msg('Loading plugins...')
    self.modules = {}
    for plugin in glob.glob(self.pluginDir + '/*/'):
      key = os.path.basename(os.path.dirname(plugin))
      self.load_plugin(key)

  def iterTriggers(self):
    h = []
    for k,m in self.modules.iteritems():    # Not the most efficient way to do this...
      for name, fn in vars(m).iteritems():
        if isinstance(fn, Trigger):
          heapq.heappush(h, fn)
    while len(h) != 0:
      yield heapq.heappop(h)

  def getSignedOnCallback(self):
    self._signedOnCallbacks.append(Defer.deferred())
    return self._signedOnCallbacks[-1]

  def signedOn(self):
    if not self.config.has_option('Bot', 'chans'): return
    for c in self.config.get('Bot', 'chans').strip('"').split(' '):
      if c: self.join(c)
    for cb in self._signedOnCallbacks:
      cb.callback(self)

  def userModes(self, channel, nick):
    mode = self.channels.get(channel, {}).get(nick, '')
    return mode
    
  def isOp(self, channel, nick):
    return '@' in self.userModes(channel, nick)

  def isHalfOp(self, channel, nick):
    return '%' in self.userModes(channel, nick)

  def isAdmin(self, channel, nick):
    return '*' in self.userModes(channel, nick)

  def isOwner(self, channel, nick):
    return '~' in self.userModes(channel, nick)

  def hasVoice(self, channel, nick):
    return '+' in self.userModes(channel, nick)

  def __setNames(self, nickList, channel):
    modes = '@*+%~&'
    ndict = {}
    for nick in nickList:
      for i,c in enumerate(nick):
        if c in modes: continue
        ndict[nick[i:]] = nick[:i]
        break
    self.channels[channel] = ndict

  def refreshIAL(self, channel):
    log.msg('Refreshing IAL for channel ' + channel)
    self.names(channel).addCallback(self.__setNames, channel)

  def names(self, channel):
    channel = channel.lower()
    cbs = self._namesCallbacks.get(channel, ([],[]))
    cbs[0].append(defer.Deferred())
    self._namesCallbacks[channel] = cbs
    self.sendLine('NAMES ' + channel)
    return cbs[0][-1]

  def irc_RPL_NAMREPLY(self, prefix, params):
    channel = params[2].lower()
    nicklist = params[3].split()
    cbs = self._namesCallbacks.get(channel, None)
    if cbs == None: return
    cbs[1].extend(nicklist)
    self._namesCallbacks[channel] = cbs

  def irc_RPL_ENDOFNAMES(self, prefix, params):
    channel = params[1].lower()
    try:
      cbs = self._namesCallbacks.pop(channel)
    except KeyError:
      return
    for cb in cbs[0]:
      cb.callback(cbs[1])

  def joined(self, channel):
    log.msg('Joined channel: ' + channel)
    self.refreshIAL(channel)

  def userJoined(self, user, channel):
    self.refreshIAL(channel)

  def userLeft(self, user, channel):
    chan = self.channels.get(channel, {})
    if user in chan:
      del chan[user]
    self.channels[channel] = chan

  def userQuit(self, user, msg):
    for chan, userdict in self.channels.items():
      if user in userdict:
        del userdict[user]
        self.channels[chan] = userdict

  def userKicked(self, kickee, channel, kicker, msg):
    chan = self.channels.get(channel, {})
    if kickee in chan:
      del chan[kickee]
    self.channels[channel] = chan

  def userRenamed(self, oldname, newname):
    for chan in self.channels:
      self.refreshIAL(chan)

  def modeChanged(self, user, channel, set, modes, args):
    self.refreshIAL(channel)

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

  def action(self, user, channel, data):
    if channel == self.nickname:
      channel, _, _ = user.partition('!')
    for fn in self.iterTriggers():
      try:
        if not fn(self, 'ACTION', user, channel, data):
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
  log.startLogging(sys.stdout)
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
  reactor.run()
