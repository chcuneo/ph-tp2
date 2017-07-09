import re
import sys
import parser
import datetime
import directions
from TTS_and_STT import speech_to_text, text_to_speech

# if len(sys.argv) != 2:
#   print('usage sdh <file>')
#   exit(1)

arrival_time = departure_time = to = ffrom = None

spoken_text = sys.argv[1]
# Paso a minuscula
spoken_text = spoken_text.lower()

# Remplazo literales por numeros sus digitos numericos
spoken_text = parser.replace_all_numbers(spoken_text)
print(spoken_text)
# ir a <dire> | estar en <dire> | esquina de <dire> | a las

ffrom = parser.get_from(spoken_text)
to = parser.get_to(spoken_text)

# Remove matched addreses to have a clean text to continue
addreses_parts = []
if ffrom:
  for part in ffrom['original']:
    addreses_parts.append(part)
if to:
  for part in to['original']:
    addreses_parts.append(part)

for part in addreses_parts:
  spoken_text = spoken_text.replace(part,' ')

# Get way of travel
travel_by = 'transit'
define_travel_by = re.search(r'\b(bondi|manejando|auto|caminando|patin|tren|subte|colectivo|moto|carro|pie)\b', spoken_text)
if define_travel_by:
  travel_by = define_travel_by.group(1)

# Get flags to know if speecher is requesting arrival time, departure time, distance, and duration
define_arrival_time = re.search(r'\b(a que hora tengo|a que hora salgo|cuando tengo|cuando salgo)\b', spoken_text)
define_departure_time = re.search(r'\b(si salgo|si me voy|saliendo)\b', spoken_text)
get_distance = re.search(r'\b(lejos|distancia)\b', spoken_text)
get_duration = re.search(r'\b(tardo|en cuanto)\b', spoken_text)

hour = parser.get_hour(spoken_text)
if hour and hour < datetime.datetime.now():
  hour = hour + datetime.timedelta(days=1)

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

print(info)
