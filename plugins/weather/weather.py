from twisted.web.client import getPage
import json

from plugin_lib import command

API_KEY = ''  # From config

CURRENT_CONDITIONS_URL = \
  'http://api.wunderground.com/api/%s/conditions/q/%s.json'

def handle_body(body, bot, channel):
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
  temp = body[u'temp_f']
  humidity = body[u'relative_humidity']
  wind = body[u'wind_mph']
  wind_dir = body[u'wind_dir']
  msg = u"%s - %s, Temp: %.1f\u2109 Humidity: %s Wind: %s %d MPH" % (loc, w_str, temp, humidity, wind_dir, wind)
  bot.say(channel, msg.encode('utf8'))

@command('weather')
def weather(bot, user, channel, args):
  """!weather [<zipcode>] # Prints out the current weather conditions for \
given zip or location of server of bot"""
  if len(args) == 0:
    location = 'autoip'
  else:
    try:  # Parse zip code
      location = str(int(args[0]))
    except ValueError:
      location = ' '.join(args)
      city, _, location = location.partition(',')
      if len(location) == 0: return
      location = location.strip().replace(' ', '_') + '/' + city.strip().replace(' ', '_')
  url = CURRENT_CONDITIONS_URL % (API_KEY, location)
  d = getPage(url, timeout=10)
  d.addCallback(handle_body, bot, channel)
  d.addErrback(bot.log.err)

def init(bot):
  global API_KEY
  API_KEY = bot.config.get('weather', 'api')