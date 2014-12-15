from twisted.web.client import getPage
import shelve
import json
import os

from plugin_lib import command

API_KEY = ''  # From config

loc_db = None

CURRENT_CONDITIONS_URL = \
  'http://api.wunderground.com/api/%s/conditions/q/%s'

def handle_body(body, bot, channel):
  wind_dir_dict = {'East': 'E', 'West': 'W', 'North': 'N', 'South': 'S' }
  body = json.loads(body)
  if u'results' in body.get(u'response', {}):  # If ambiguous
    print json.dumps(body[u'response'], sort_keys=True, indent=4, separators=(',', ': '))
    station_id = body[u'response'][u'results'][0][u'zmw'].encode('utf8')
    url = CURRENT_CONDITIONS_URL % (API_KEY, 'zmw:' + station_id)
    d = getPage(url, timeout=10)
    d.addCallback(handle_body, bot, channel)
    d.addErrback(bot.log.err)
    return
  body = body[u'current_observation']
  loc = body[u'display_location'][u'full']
  w_str = body[u'weather']
  if 'snow' in w_str.lower():
    w_str = u'\u2744 ' + w_str
  elif 'rain' in w_str.lower():
    w_str = u'\u2602 ' + w_str
  elif 'cloud' in w_str.lower():
    w_str = u'\u2601 ' + w_str
  temp = body[u'temp_f']
  feels_like = float(body[u'feelslike_f'])
  humidity = body[u'relative_humidity']
  wind = body[u'wind_mph']
  wind_dir = body[u'wind_dir']
  wind_dir = wind_dir_dict.get(wind_dir, wind_dir)
  msg = u"%s - %s Temp: %.1f\u2109(%.1f\u2109) Hum: %s Wind: %s %d MPH" % (loc, w_str, temp, feels_like, humidity, wind_dir, wind)
  bot.say(channel, msg.encode('utf8'))

# First, look in the db for the user's location
# if not found, try the user's host -> ip -> geo
#  replace localhost with connected server's ip
# default to connected server's ip
def get_user_location(host, default):
  import socket
  # default is probably cached by the file system, so ignore it
  ip = socket.gethostbyname(default)
  if host == 'localhost':
    host = ip
  try:
    ip = socket.gethostbyname(host)
  except socket.gaierror:
    pass
  return ip

@command('weather')
def weather(bot, user, channel, args):
  """!weather [<zipcode>] # Prints out the current weather conditions for \
given zip or location of server of bot"""
  global loc_db
  nick, _, hostmask = user.partition('!')
  username, _, host = user.partition('@')
  change = len(args) > 0 and args[0] == 'default'
  if change: args.pop(0)
  if len(args) == 0:
    location = None if change else loc_db.get(username, None)
    if location == None:
      location = 'autoip.json?geo_ip=' + get_user_location(host, bot.hostname)
  else:
    try:  # Parse zip code
      location = str(int(args[0])) + '.json'
    except ValueError:
      location = ' '.join(args)
      city, _, location = location.partition(',')
      if len(location) == 0: return
      location = location.strip().replace(' ', '_') + '/' + city.strip().replace(' ', '_')
      location += '.json'
  if change:
    loc_db[username] = location
    loc_db.sync()
  url = CURRENT_CONDITIONS_URL % (API_KEY, location)
  d = getPage(url, timeout=10)
  d.addCallback(handle_body, bot, channel)
  d.addErrback(bot.log.err)

def init(bot):
  global API_KEY, loc_db
  API_KEY = bot.config.get('weather', 'api')
  WEATHER_DB_FILE = '~/.config/glitchbot/weather.shelve'
  if bot.config.has_option('weather', 'db'):
    WEATHER_DB_FILE = bot.config.get('weather', 'db')
  loc_db = shelve.open(os.path.expanduser(WEATHER_DB_FILE))
