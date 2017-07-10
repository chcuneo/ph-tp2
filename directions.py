import requests
import grequests
import googlemaps
import bisect
import re
import time
import datetime
from usig_normalizador_amba import NormalizadorAMBA
import os.path
import pickle
from unidecode import unidecode

if os.path.isfile('nd.pkl'):
  with open('nd.pkl', 'rb') as f:
    nd = pickle.load(f)
else:
  nd = NormalizadorAMBA(include_list=['caba'])

DEFAULT_FROM = { 'parsed': 'Facultad de Ciencias Exactas y Naturales - UBA, Av. Int. Cantilo, Buenos Aires, Argentina', 'text': 'ciudad universitaria' }

gmaps = googlemaps.Client(key='AIzaSyDSJHXfqUJUSSlv5mt1Gx6fIwlTgWrkzgg')
minutes_interval = { 'bounds': [6, 13, 17, 23, 27, 33, 37, 43, 47, 53, 59], 'names': ['5', '10', 'cuarto', '20', '25', 'media', '35', '40', '45', '50', '55'] }
translate = { 'day': 'dia', 'hour': 'hora', 'min': 'minuto'}
get_travel_by = {
  'transit': 'transit',
  'driving': 'driving',
  'walking': 'walking',
  'bicycling': 'bicycling',
  'bondi': 'transit',
  'manejando': 'driving',
  'auto': 'driving',
  'caminando': 'walking',
  'patin': 'walking',
  'tren': 'transit',
  'subte': 'transit',
  'colectivo': 'transit',
  'moto': 'driving',
  'carro': 'driving',
  'pie': 'walking',
  'bici': 'bicycling'
}

def addresses_url(strings):
  urls = []
  for string in strings:
    urls.append('http://servicios.usig.buenosaires.gob.ar/normalizar/?direccion={}, caba'.format(re.sub(r'(\d)\s+(?=\d)', r'\1', string)))
  rs = (grequests.get(u) for u in urls)
  rs = grequests.map(rs)
  guesses = []
  for s, r in zip(strings, rs):
    possibilities = r.json()['direccionesNormalizadas']
    if len(possibilities) == 0:
      guesses.append(None)
      continue
    usig_address = possibilities[0]
    res = { 'street_code': usig_address['cod_calle'], 'coordinates': usig_address['coordenadas'] }
    if usig_address['cod_calle_cruce']:
      res['street_code_2'] = usig_address['cod_calle_cruce']
      res['text'] = '{} y {}'.format(pretty_street(usig_address['nombre_calle']), pretty_street(usig_address['nombre_calle_cruce']))
    else:
      res['number'] = usig_address['altura']
      res['text'] = '{} {}'.format(pretty_street(usig_address['nombre_calle']), res['number'])
    guesses.append(res)
  return guesses

def addresses_nd(strings):
  guesses = []
  for s in strings:
    possibilities = nd.normalizar(re.sub(r'(\d)\s+(?=\d)', r'\1', s))
    if len(possibilities) == 0:
      guesses.append(None)
      continue
    usig_address = possibilities[0]
    res = { 'street_code': usig_address.calle.codigo, 'parsed': usig_address.toString() }
    if usig_address.cruce:
      res['street_code_2'] = usig_address.cruce.codigo
      res['text'] = '{} y {}'.format(pretty_street(usig_address.calle.nombre), pretty_street(usig_address.cruce.nombre))
    else:
      res['number'] = usig_address.altura
      res['text'] = '{} {}'.format(pretty_street(usig_address.calle.nombre), usig_address.altura)
    guesses.append(res)
  return guesses

def pretty_number(number):
  return (number - (number % 100)) if number > 99 else number

def pretty_street(street):
  if street.find('AV.') != -1:
    return 'Avenida {}'.format(street).replace(' AV.','').title()
  return street.title()

def barrio(x, y):
  url = 'http://ws.usig.buenosaires.gob.ar/datos_utiles?x={}&y={}'.format(x, y)
  r = requests.get(url)
  return r.json()['barrio']

def travel_time(ffrom, to, by='transit', departure_at=None, arrival_at=None):
  travel_params = {}
  if arrival_at:
    travel_params['arrival_time'] = arrival_at
  elif departure_at:
    travel_params['departure_time'] = departure_at
  travel_params['mode'] = by
  directions_result = gmaps.directions(ffrom, to, **travel_params)
  return directions_result

def pretty_duration(time_string):
  for k, v in translate.items():
    time_string = time_string.replace(k, v)
  parts = time_string.split(' ')
  if len(parts) == 6:
    return '{} {}, {} {} y {} {}'.format(*parts)
  elif len(parts) == 4:
    return '{} {} y {}'.format(*parts[:2], pretty_minutes(parts[2]))
  elif len(parts) == 2:
    return '{} {}'.format(*parts)

def pretty_minutes(minutes):
  return minutes_interval['names'][bisect.bisect_left(minutes_interval['bounds'], int(minutes))]

def pretty_time(time):
  now = datetime.datetime.now()
  hour = time.hour
  if time.hour > 12:
    hour -= 12
  if time.hour > 19:
    time_of_day = 'de la noche'
  elif time.hour > 12:
    time_of_day = 'de la tarde'
  else:
    time_of_day = 'de la mañana'
  minutes = pretty_minutes(time.minute)
  output = []
  output.append(str(hour))
  if minutes == 'media' or minutes == 'cuarto':
    output.append('y {}'.format(minutes))
  elif time.minute != 0:
    output.append(str(minutes))
  if now.day != time.day or (now.hour < 12 and now.hour < time.hour):
    output.append(time_of_day)
  return ' '.join(output)

def travel_info(ffrom, to, by='bondi', departure_at=None, arrival_at=None):
  travel_by = get_travel_by[by]
  if ffrom == None:
    ffrom = DEFAULT_FROM
  if ffrom.get('coordinates', None) == None:
    from_address = ffrom['parsed']
    to_address = to['parsed']
  else:
    from_address = '{},{}'(ffrom['coordinates']['y'], ffrom['coordinates']['x'])
    to_address = '{},{}'(to['coordinates']['y'], to['coordinates']['x'])
  routes = travel_time(
                        from_address,
                        to_address,
                        by=travel_by,
                        departure_at=departure_at,
                        arrival_at=arrival_at
                      )
  if len(routes) == 0:
    return None
  route = routes[0]['legs'][0]
  info = {}
  # info['to_barrio'] = barrio(requested_address['coordinates']['x'], requested_address['coordinates']['y'])
  info['from'] = ffrom['text']
  info['to'] = to['text']
  info['duration'] = pretty_duration(route['duration']['text'])
  if departure_at:
    info['arrival_time'] = departure_at + datetime.timedelta(seconds=route['duration']['value'])
    info['departure_time'] = departure_at
  elif arrival_at:
    info['departure_time'] = arrival_at - datetime.timedelta(seconds=route['duration']['value'])
    info['arrival_time'] = arrival_at
  else:
    info['arrival_time'] = datetime.datetime.now() + datetime.timedelta(seconds=route['duration']['value'])
    info['departure_time'] = datetime.datetime.now()
  info['distance'] = route['distance']['text']
  info['travel_by'] = travel_by
  return info
