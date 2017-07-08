import re
import datetime
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
  'media': 30 ,
  'cuarto': 15,
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
  # '33 orientales al 200' o '33 orientales 200'
  specific = re.match(r'^((?:[0-9]* )?(?:(?!al |y )[a-z]+ )+)(?:al )?([0-9]+)(?:$| )', string)
  if specific:
    possibles.append(specific.group(1) + specific.group(2))
  # '33 orientales y 9 de julio'
  intersection = re.match(r'^((?:[0-9]* )?(?:(?!al |y )[a-z]+ )+)(?:y)((?: [0-9]*)?(?:(?! al| y) [a-z]+)+)(?: [0-9]|$| y|)', string)
  if intersection:
    possibles.append('{}y {}'.format(intersection.group(1), intersection.group(2)))
  return possibles
