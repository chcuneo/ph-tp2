import re
import datetime
import directions
from pytrie import SortedStringTrie as Trie

numeros = {
  'cero': 0,
  'diez': 10,
  'once': 11,
  'doce': 12,
  'trece': 13,
  'catorce': 14,
  'quince': 15,
  'dieciseis': 16,
  'diez y seis': 16,
  'diecisiete': 17,
  'diez y siete': 17,
  'dieciocho': 18,
  'diez y ocho': 18,
  'diecinueve': 19,
  'diez y nueve': 19,
  'veintiuna': 21,
  'veintiuno': 21,
  'veintiun': 21,
  'veintidos': 22,
  'veintitres': 23,
  'veinticuatro': 24,
  'veinticinco': 25 ,
  'veintiseis': 26 ,
  'veintisiete': 27 ,
  'veintiocho': 28 ,
  'veintinueve': 29 ,
  'medianoche': 0 ,
  'mediodia': 12 ,
  'veinte': 20,
  'treinta': 30 ,
  'cuarenta': 40 ,
  'cincuenta': 50 ,
  'sesenta': 60,
  'setenta': 70,
  'ochenta': 80,
  'noventa': 90,
  # 'media': 30 ,
  # 'cuarto': 15,
  'do': 2,
  'tre': 3,
  'quin': 5,
  'sei': 6,
  'sete': 7,
  'nove': 9,
  }
for number, text in [(1, 'un'), (1, 'una'), (1, 'uno'), (2, 'dos'), (3, 'tres'), (4, 'cuatro'), (5, 'cinco'), (6, 'seis'), (7, 'siete'), (8, 'ocho'), (9, 'nueve')]:
  numeros[text] = number
  numeros['treinti{}'.format(text)] = 30 + number
  numeros['treinta y {}'.format(text)] = 30 + number
  numeros['cuarenti{}'.format(text)] = 40 + number
  numeros['cuarenta y {}'.format(text)] = 40 + number
  numeros['cincuenti{}'.format(text)] = 50 + number
  numeros['cincuenta y {}'.format(text)] = 50 + number
  numeros['sesenti{}'.format(text)] = 60 + number
  numeros['sesenta y {}'.format(text)] = 60 + number
  numeros['setenti{}'.format(text)] = 70 + number
  numeros['setenta y {}'.format(text)] = 70 + number
  numeros['ochenti{}'.format(text)] = 80 + number
  numeros['ochenta y {}'.format(text)] = 80 + number
  numeros['noventi{}'.format(text)] = 90 + number
  numeros['noventa y {}'.format(text)] = 90 + number

numeros = Trie(numeros)

multiplicadores = Trie({
  'mil': 1000,
  'ientos': 100,
  'cientos': 100,
  'ciento': 100,
  'cientas': 100,
  'cienta': 100,
  'cien': 100
})

momento_del_dia = Trie({ 'de la noche': 'pm', 'de la mañana': 'am', 'del mediodia': 'pm', 'de la tarde': 'pm' })

time_of_day_to_sum = {
  'noche': 12,
  'tarde': 12,
  'mañana': 0,
  'madrugada': 0,
}

def replace_all_numbers(string):
  index = 0
  string = string.lower()
  while index < len(string) and index != -1:
    match = get_number(string[index:])
    if match[0]:
      pre = string[:index]
      number = str(match[0])
      post = string[(index + match[1]):]
      string = '{} {} {}'.format(pre, number, post)
      index = len(pre) + len(number)
    index = string.find(' ', index + 1)
  return string

def find_all_numbers(string):
  numbers = []
  index = 0
  while index < len(string) and index != -1:
    match = get_number(string[index:])
    if match[0]:
      numbers.append({ 'start': index, 'end': index + match[1], 'number': match[0]})
      index += match[1] - 2
      print(string[index:])
    index = string.find(' ', index + 1)
  return numbers

# No estoy orgulloso del codigo de este metodo
def get_number(string):
  values = {1000: None, 100: None, 10: None}

  def cant_update(multiplier):
    filled = values[multiplier] != None
    less_filled = any([values[m] != None for m in [1000, 100, 10] if m < multiplier])
    return filled or less_filled

  original = string
  string = string.lower()
  while len(string) > 0:
    working_string = string.lstrip()
    match_num, number = numeros.longest_prefix_item(working_string, default=('', None))
    working_string = working_string[len(match_num):].lstrip()
    match_mul, multiplier = multiplicadores.longest_prefix_item(working_string, default=('', None))
    working_string = working_string[len(match_mul):].lstrip()
    if match_mul == '' and match_num == '':
      break
    if match_mul == '' and match_num != '':
      if cant_update(10):
        break
      values[10] = number
    if match_mul != '' and match_num == '':
      if cant_update(multiplier):
        break
      values[multiplier] = 1
    if match_mul != '' and match_num != '':
      if cant_update(multiplier):
        break
      values[multiplier] = number
    string = working_string

  number = None
  not_found = all(v is None for v in list(values.values()))
  if not_found:
    return (None, 0)
  number = 0
  if values[10] != None:
    number += values[10]
  if values[100] != None:
    number += values[100] * 100
  if values[1000] != None:
    number += values[1000] * 1000

  return (number, len(original) - len(string))

def to_time_of_day(hour, time_of_day):
  if time_of_day == 'pm' and hour < 12:
    return hour + 12
  return hour

def get_time(string):
  hour = minute = time_of_day = None
  match, item = numeros.longest_prefix_item(string, default=(None,None))
  # No match
  if match == None:
    return None
  hour = item
  # Remove hour
  string = string[len(match):].lstrip()
  # Remove ' y ' between hour an minute
  if len(string) > 0:
    string = string.lstrip([' ', 'y'])
  match, item = numeros.longest_prefix_item(string, default=(None,None))
  if match:
    minute = item
  string = string[len(match):].lstrip()

  match, item = momento_del_dia.longest_prefix_item(string, default=(None,None))
  if match:
    time_of_day = item

  if time_of_day and hour:
    hour = to_time_of_day(hour, time_of_day)
  if minute != None:
    return datetime.time(hour, minute)
  return datetime.time(hour)

def get_addresses(string):
  possibles = []
  # Exact address: <name of street> [al] <altura>. For example '33 orientales al 200' or '33 orientales 200'
  specific = re.match(r'^(?=(((?:[0-9]* )?(?:(?!al |y )[A-zÀ-ú]+ )+)(?:al )?((?:[0-9]+ )+))(?:$| ))', string)
  if specific:
    possibles.append({ 'match': specific.group(2) + specific.group(3), 'original': specific.group(1)})
  # Intersection: <name of street> y <name of street> '33 orientales y 9 de julio'
  intersection = re.match(r'^(?=(((?:[0-9]* )?(?:(?!al |y )[A-zÀ-ú]+ )+)(?:y)((?: [0-9]*)?(?:(?! al| y) [A-zÀ-ú]+)+))(?= [0-9]|$| y|))', string)
  if intersection:
    possibles.append({ 'match': '{}y {}'.format(intersection.group(2), intersection.group(3)), 'original': intersection.group(1) })
  return possibles

def get_from(string):
  # This regex finds possible addresses delimited by some delimiters I found in the language for a departure place
  possible_from = re.findall(r'\b(?=(?:desde |de )((?:(?!(?:manejando|caminando|a|en|tipo|las|hasta|como|si|cuanto) )\w+ )+)(?=(?:manejando|caminando|a|en|tipo|las|hasta|como|si|cuanto) |$))', string)
  potential_from = []
  for possible in possible_from:
    addresses = get_addresses(possible)
    potential_from.append(addresses)
  # Flatten list
  potential_from = [item for sublist in potential_from for item in sublist]
  real_addreses = directions.addresses_nd([i['match'] for i in potential_from])
  potential_from = [{'match': z[1], 'original': z[0]['original']} for z in zip(potential_from, real_addreses) if z[1] != None]
  return None if len(potential_from) == 0 else max(potential_from, key= lambda x: len(x['match']['text']))

def get_to(string):
  # This regex finds possible addresses delimited by some delimiters I found in the language for a destination, the main difference with the other is the 'hasta' with 'desde'.
  # Then it considers el 'estoy de' for the case 'a cuanto estoy de'
  possible_to = re.findall(r'\b(?=(?:hasta |a |en |estoy de )((?:(?!(?:manejando|caminando|a|en|tipo|las|desde|como|si|cuanto) )\w+ )+)(?=(?:manejando|caminando|a|en|tipo|las|desde|como|si|cuanto) |$))', string)
  potential_to = []
  for possible in possible_to:
    addresses = get_addresses(possible)
    potential_to.append(addresses)
  # Flatten list
  potential_to = [item for sublist in potential_to for item in sublist]
  real_addreses = directions.addresses_nd([i['match'] for i in potential_to])
  potential_to = [{'match': z[1], 'original': z[0]['original']} for z in zip(potential_to, real_addreses) if z[1] != None]
  return None if len(potential_to) == 0 else max(potential_to, key= lambda x: len(x['match']['text']))

def get_hour(string):
  now = datetime.datetime.now()
  string = string.replace(':', ' y ')
  # This one finds delta of times '1 hora 2 minutos', '1 hora' or '1 hora y 2' for example
  duration = re.search(r'\b([0-9][0-9]?) horas?(?: y)?(?: ([0-9][0-9]|(?:media|cuarto)?)(?: minutos?)?)?\b', string)
  if duration:
    hours = int(duration.group(1))
    minutes = duration.group(2)
    if minutes == '' or minutes == None:
      minutes = 0
    if minutes == ' media':
      minutes = 30
    if minutes == ' cuarto':
      minutes = 15
    minutes = int(minutes)
    return now + datetime.timedelta(hours=hours, minutes=minutes)
  duration = re.search(r'\b([0-9][0-9]?) minutos?\b', string)
  if duration:
    minutes = int(duration.group(1))
    return now + datetime.timedelta(minutes=minutes)
  duration = re.search(r'\bmedia hora\b', string)
  if duration:
    return now + datetime.timedelta(minutes=30)
  # This one finds exact times '2 y media a la tarde' for example, where 'y', 'media'(los minutos) and 'a la tarde' are optional
  times = re.search(r'\b(([0-9][0-9]?\b)(?: y\b)?( [0-9][0-9]?\b| (?:media|cuarto)\b)?(?: (?:del|de la|de el)? (noche|tarde|madrugada|mañana)\b)?)', string)
  if times:
    hour = int(times.group(2))
    minutes = times.group(3)
    if minutes == '' or minutes == None:
      minutes = 0
    if minutes == ' media':
      minutes = 30
    if minutes == ' cuarto':
      minutes = 15
    minutes = int(minutes)
    if times.group(4):
      hour += time_of_day_to_sum[times.group(4)]
    time = now.replace(hour=hour, minute=minutes, second=0)
    if times.group(4) == None and hour <= 12:
      if now.hour >= 12 and (now.hour - 12 <= hour or ((now.hour - 12) == hour and now.minute > minutes)):
        time = time + datetime.timedelta(hours=12)
      elif now.hour < 12 and (now.hour > hour or (now.hour == hour and now.minute > minutes)):
        time = time + datetime.timedelta(hours=12)
    return time
  moment = re.search(r'\b(mediodia|medianoche)\b', string)
  if moment:
    if moment.group(1) == 'mediodia':
      hour = 12
    else:
      hour = 00
    return now.replace(hour=hour, second=0)
  return None


