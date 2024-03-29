import datetime
import re
import sys
import parser
import directions
import subprocess
from TTS_and_STT import speech_to_text_google, speech_to_text, text_to_speech
import random
from unidecode import unidecode

def parse(spoken_text):
  arrival_time = departure_time = to = ffrom = None

  # Paso a minuscula
  spoken_text = unidecode(spoken_text.lower()) + ' '

  # Remplazo literales por numeros sus digitos numericos
  spoken_text = parser.replace_all_numbers(spoken_text)
  # ir a <dire> | estar en <dire> | esquina de <dire> | a las

  to = parser.get_to(spoken_text)
  if to == None:
    return 'no entendi adonde queres ir, o capaz la direccion no existe'
  spoken_text = spoken_text.replace(to['original'],'')
  ffrom = parser.get_from(spoken_text)
  if ffrom:
    spoken_text = spoken_text.replace(ffrom['original'],'')

  # Remove matched addreses to have a clean text to continue

  # Get way of travel
  travel_by = 'bondi'
  define_travel_by = re.search(r'\b((?:a |en )?(bondi|manejando|auto|caminando|patin|tren|subte|colectivo|moto|carro|pie))\b', spoken_text)
  if define_travel_by:
    travel_by = define_travel_by.group(2)

  # Get flags to know if speecher is requesting arrival time, departure time, distance, and duration
  define_arrival_time = re.search(r'\b(a que hora tengo|a que hora salgo|cuando tengo|cuando salgo)\b', spoken_text)
  define_departure_time = re.search(r'\b(si salgo|si me voy|saliendo|yendo a las?)(?! de| desde)\b', spoken_text)
  get_distance = re.search(r'\b(lejos|distancia)\b', spoken_text)
  get_duration = re.search(r'\b(tardo|((en|a) )?cuanto)\b', spoken_text)

  hour = parser.get_hour(spoken_text)
  if hour and hour < datetime.datetime.now():
    hour = hour + datetime.timedelta(days=1)
    print(hour)
  travel_params = {
    'by': travel_by,
  #  'departure_at': ,
  #  'arrival_at':
  }

  if define_departure_time and hour:
    travel_params['departure_at'] = hour
  elif define_arrival_time and hour:
    travel_params['arrival_at'] = hour

  from_address = None if ffrom == None else ffrom['match']
  to_address = to['match']

  info = directions.travel_info(from_address, to_address, **travel_params)

  pre = []
  pos = []

  if info == None:
    return 'no encontre una ruta para ir a {} desde aca en {}'.format(to['match'], travel_by)
  if ffrom != None:
    pos.append('saliendo desde {}'.format(info['from']))
  if define_travel_by:
    chance = random.random()
    if chance < 0.29:
      s = 'yendo'
    else:
      s = 'si vas'
    pos.append('{} {}'.format(s, define_travel_by.group(1)))
  if get_distance:
    pre.append('estas a {} de'.format(info['distance']))
  if get_duration and define_arrival_time == None and get_distance == None:
    chance = random.random()
    if chance < 0.33:
      pre.append('vas a tardar {} en llegar a'.format(info['duration']))
    elif chance < 0.66:
      pre.append('te va a llevar {} llegar a'.format(info['duration']))
    else:
      pre.append('vas a estar en {} en'.format(info['duration']))
  if define_departure_time and define_arrival_time == None and hour and get_distance == None:
    chance = random.random()
    if chance < 0.33:
      s = 'si salis'
    elif chance < 0.66:
      s = 'si vas'
    else:
      s = 'si te vas'
    pos.append('{} {}'.format(s, directions.pretty_time(info['departure_time'])))
  elif define_arrival_time and hour and get_distance == None:
    chance = random.random()
    if chance < 0.33:
      pre.append('si queres llegar a')
    elif chance < 0.66:
      pre.append('si queres estar en')
    else:
      pre.append('si tenes que estar en')
    pos.append('a las {}'.format(directions.pretty_time(info['arrival_time'])))
    chance = random.random()
    if info['departure_time'] < datetime.datetime.now():
      if chance < 0.33:
        s = 'tendrias que haber salido'
      elif chance < 0.66:
        s = 'tenias que salir'
      else:
        s = 'deberias haberte ido'
    else:
      if chance < 0.33:
        s = 'vas a tener que salir'
      elif chance < 0.66:
        s = 'tenes que salir'
      else:
        s = 'andate'
    pos.append('{} {}'.format(s, directions.pretty_time(info['departure_time'])))
  if get_duration == None and define_arrival_time == None and get_distance == None and define_departure_time == None:
    pre.append('vas a llegar {} a'.format(directions.pretty_time(info['arrival_time'])))

  output = pre + [info['to']] + pos
  output = ' '.join(output)

  return output

def infinite_parse():
  while True:
    input("Press Enter to start recording...")
    p = subprocess.Popen(['sox', '-d', '--channels=1', '--bits=16', 'speech.flac'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    input("Press Enter to stop recording...")
    p.terminate()
    spoken_text = speech_to_text_google('speech.flac')
    print(spoken_text)
    output = parse(spoken_text)
    print(output)
    text_to_speech("output.wav", output, rate_change="+0%", f0mean_change="+0%")
    subprocess.call('mplayer output.wav 1> /dev/null 2> /dev/null', shell=True)

if len(sys.argv) != 2:
  infinite_parse()
else:
  print(parse(sys.argv[1]))
