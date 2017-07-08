import re
import sys
import parser
import directions
from TTS_and_STT import speech_to_text, text_to_speech

# if len(sys.argv) != 2:
#   print('usage sdh <file>')
#   exit(1)

arrival_time = departure_time = to = ffrom = travel_by = None
spoken_text = sys.argv[1]
# Paso a minuscula
spoken_text = spoken_text.lower()

# Remplazo literales por numeros sus digitos numericos
spoken_text = parser.replace_all_numbers(spoken_text)
print(spoken_text)
# ir a <dire> | estar en <dire> | esquina de <dire> | a las
possible_from = re.findall(r'(?:desde |de )((?:(?!a |en |tipo |las |hasta |como |si )\w+ )+)(?:a |en |tipo |las |hasta |como |si |$)', spoken_text)
possible_to = re.findall(r'(?:hasta |a |en )((?:(?!a |en |tipo |las |desde |como |si )\w+ )+)(?:a |en |tipo |las |desde |como |si |$)', spoken_text)

print(possible_from)
print(possible_to)

potential_from = []
for possible in possible_from:
  addresses = parser.get_addresses(possible)
  potential_from.append(addresses)
# Flatten list
potential_from = [item for sublist in potential_from for item in sublist]

potential_to = []
for possible in possible_to:
  addresses = parser.get_addresses(possible)
  potential_to.append(addresses)
# Flatten list
potential_to = [item for sublist in potential_to for item in sublist]

potential_from = directions.addresses_nd(potential_from)
potential_to = directions.addresses_nd(potential_to)

ffrom = None if len(potential_from) == 0 else max(potential_from, key= lambda x: len(x['text']))
to = None if len(potential_to) == 0 else max(potential_to, key= lambda x: len(x['text']))

info = directions.travel_info(ffrom, to)

print(info)

define_arrival_time = re.match(r'a que hora tengo|a que hora salgo|cuando tengo|cuando salgo', spoken_text)
if define_arrival_time:
  match = re.match(r'(?:a las|tipo|a la) (.*)^', spoken_text)
  if match:
    arrival_time = parser.get_time(match.group(1))

define_departure_time = re.match(r'(?:si salgo|si me voy|saliendo) (?: a las|tipo) (.*)^', spoken_text)
if define_departure_time:
  departure_time = parser.get_time(define_departure_time.group(1))

