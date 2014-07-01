import random
from plugin_lib import command

dancers=[
    '\\o/ ',
    ' |  ',
    '/ \\ ',
    '\\o  ',
    ' |\\ ',
    '/ \\ ',
    ' o/ ',
    '/|  ',
    '/ \\ ',
    'o// ',
    ' |  ',
    '//  ',
    '\\\\o ',
    ' |  ',
    ' \\\\ ', 
    '\\\\o ',
    ' |  ',
    '//  ',
    'o// ',
    ' |  ',
    ' \\\\ ',
    '_o_',
    ' | ',
    '/ \\',
    '_o/',
    ' | ',
    '/ \\',
    '\\o_',
    ' | ',
    '/ \\',
    '_o_',
    ' | ',
    '// ',
    '_o_',
    ' | ',
    ' \\\\',
    '\\o_',
    ' | ',
    '// ',
    '\\o_',
    ' | ',
    ' \\\\',
    '_o/',
    ' | ',
    '// ',
    '_o/',
    ' | ',
    ' \\\\',]

@command('dance')
def dance(bot, user, channel, args):
  """!dance [<N>] # Like you've never done before!"""
  num = 1
  if len(args) != 0:
    try:
      num = int(args[0])
    except ValueError:
      pass
  str1, str2, str3 = '','',''
  for _ in xrange(min(num, 10)):
    i = int((len(dancers)/3.0)*random.random())
    str1 += dancers[i*3] + ' '
    str2 += dancers[i*3+1] + ' '
    str3 += dancers[i*3+2] + ' '
  bot.say(channel, str1)
  bot.say(channel, str2)
  bot.say(channel, str3)
