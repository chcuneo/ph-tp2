import pickle
import requests

names = {}
streets = requests.get('http://servicios.usig.buenosaires.gob.ar/callejero?full=1').json()
streets = [x[2] for x in streets]
for street in streets:
  striped_street = [char for char in street if not char in ['(', ')', '.', '-', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']]
  striped_street = ''.join(striped_street)
  for word in striped_street.split(' '):
    names[word] = True

names = ' '.join(names.keys()).lower()

with open('streets_caba.pkl', 'wb') as f:
  pickle.dump(names, f, pickle.HIGHEST_PROTOCOL)
