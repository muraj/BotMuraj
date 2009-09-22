"""Config Constants"""
#!/usr/bin/python
# -*- coding: utf-8 -*-
SERVER	=	'csc.nmu.edu'
PORT	=	6667
NICK	=	'BotMuraj2'
CHAN	=	['#test']
MASTER	=	'muraj'

import socket, asyncore, asynchat, sys, re, imp, glob, os, traceback, logging
class Bot(asynchat.async_chat):
	def __init__(self, nick, chs, master, log=None, log_level=None):
		self.nick=nick
		self.master=master
		asynchat.async_chat.__init__(self)
		self.set_terminator('\r\n')
		self.buffer=''
		self.origin=re.compile(r'([^!]*)!?([^@]*)@?(.*)')
		self.chans=[chan for chan in chs]
		if not log == None:
			logging.basicConfig(level=log_level, filename=log, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		os.chdir(os.path.split(os.path.abspath(__file__))[0])	#Keeping everything relative to the root directory structure
		self.mods={}
		paths=glob.glob('./modules/*.py')
		for f in paths:			#Error checking here.
			self.addhook(self.fileimport(f))
		for k,l in self.mods.iteritems():
			self.mods[k]=sorted(l, lambda m1,m2: m1.PRIORITY-m2.PRIORITY)
	def addhook(self, mod):
		if mod==None: return None
		if not self.mods.has_key(mod.COMMAND):
			self.mods[mod.COMMAND]=[]
		self.mods[mod.COMMAND].append(mod)
		return mod
	def modimport(self, name):	#Imports and/or Reloads modules
		return self.fileimport("./modules/%s.py" % name)
	def fileimport(self, fn):
		if not fn.endswith('.py'):
			return None
		f=file(fn,'r')
		desc=('.py','r',imp.PY_SOURCE)
		m=imp.load_module(os.path.split(fn[:-3])[1], f, fn, desc)
		if self.checkmod(m):
			logging.info('Loaded Module: %s' % m.__name__)
			return m
		else:
			logging.warning('Module is not valid!: %s' % m.__name__)
			return None
	def connectServer(self, host, port=6667):
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((host,port))
	def run(self):
		asyncore.loop()
	def collect_incoming_data(self, data):
		self.buffer+=data
	def found_terminator(self):
		line = self.buffer
		self.buffer=''
		if line.startswith(':'):
			source, line = line[1:].split(' ',1)
		else: source=''
		nick, user, server = self.origin.match(source).groups()
		if ' :' in line:
			arg, text=line.split(':', 1)
		else: arg, text= line, ''
		arg=arg.split()
		arg.append(user)
		arg.append(nick)
		if arg[0] == 'PING':
			self.write('PONG', [], text=text)
			return
		_directed = False
		if arg[0] == 'PRIVMSG':
			if text.startswith(self.nick+':'):
				text=text.split(':',1)[1][1:]
				_directed = True
			if arg[1]==self.nick:
				arg[1]=arg[-1]
				_directed = True
			if self.nick in text: _directed = True	#Not sure I want this.
		if not self.mods.has_key(arg[0]): return
		for m in self.mods[arg[0]]:
			if re.match(m.RULE, text):
				try:
					if arg[0] == "PRIVMSG":	#yes, I know...
						if not((_directed and m.DIRECTED&1) or (not _directed and m.DIRECTED&2)):
							continue	#Skip if not directed and is supposed to be
					if not m.PROCESS(self, arg, text): break
				except:
					e=sys.exc_info()
					logging.error('Input: %s, \"%s\"', arg, text, exc_info=e)
					if arg[0] == 'PRIVMSG':
						self.mesg('I am terribly sorry, but it seems that I have had an exception while parsing your message.  Please review my logs to see why.', arg[1])
					break
	def handle_connect(self):
		self.write('NICK',[self.nick])
		self.write('USER',[self.nick,self.nick,self.nick,self.nick])
		self.write('JOIN',[ ','.join(self.chans) ])
	def handle_close(self):
		logging.critical('Socket Closed')
		exit(1)
	def log(self, msg, lvl='debug'):
		ll={'critical': logging.CRITICAL,
			'error': logging.ERROR,
			'warning': logging.WARNING,
			'info':	logging.INFO,
			'debug': logging.DEBUG }.get(lvl,logging.NOTSET)
		logging.log(ll,msg)
	def write(self, cmd, args, text=None):
		args=' '.join([arg.replace('\r\n','').replace('\t','   ') for arg in args])
		if isinstance(args,unicode): args=args.encode('utf-8')
		if text != None:
			text=text.replace('\r\n','').replace('\t','   ')
			if isinstance(text,unicode): text=text.encode('utf-8')
			self.push(cmd+' '+args+' :'+text+'\r\n')
		else: self.push(cmd+' '+args+'\r\n')
	def checkmod(self, m):
		if not hasattr(m,'RULE'): return False
		if not hasattr(m,'PRIORITY'): return False
		if not (hasattr(m,'PROCESS') and callable(m.PROCESS)): return False
		if not hasattr(m,'COMMAND'): return False
		if not hasattr(m,'DIRECTED'): m.DIRECTED = True	#Default to directed
		if hasattr(m,'INIT') and callable(m.INIT): 
			m.INIT(self)	#Optional initialization
		return True
	def mesg(self, text, chan, user=''):
		if not user=='': self.write('PRIVMSG',[chan], user+': '+text)
		else: self.write('PRIVMSG',[chan], text)
	def joinchan(self, chan):
		self.write('JOIN',[chan])
		self.chans.append(chan)
		#Information caching needed here.
if __name__=='__main__':
	import optparse
	parser = optparse.OptionParser()
	parser.add_option('-l','--logging-level',help='Logging Level')
	parser.add_option('-f','--logging-file',help='Logging Filename')
	(options, args) = parser.parse_args()
	ll={'critical': logging.CRITICAL,
		'error': logging.ERROR,
		'warning': logging.WARNING,
		'info':	logging.INFO,
		'debug': logging.DEBUG }.get(options.logging_level,logging.NOTSET)
	bot=Bot(NICK, CHAN, MASTER, log=options.logging_file, log_level=ll)
	bot.connectServer(SERVER, PORT)
	bot.run()
