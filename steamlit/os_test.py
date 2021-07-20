# import os

# BASEDIR = os.getcwd()
# PATH = os.path.join(BASEDIR, '../page/ui/estimation.json')

# #PATH = os.path.abspath(os.path.join(PATH, '..'))
# PATH = os.path.abspath(PATH)

# print(PATH)
# print(os.path.isfile(PATH))
# print(PATH.__class__)

import requests
import json

SESSION = requests.Session()
URL = 'http://localhost:5000/api/content/model'
PARAMS = {
    'country':'Украина',
    'pov':'Народ'
}
#PARAMS = None
TIMEOUT = (0.01, 0.01)
try:
    RESPONSE = SESSION.get(url=URL, params=PARAMS, timeout= TIMEOUT)
except requests.RequestException:
    RESPONSE = None
if RESPONSE:
    RESPONSE.encoding = 'utf-8'
# print(RESPONSE.text)
    print(json.loads(RESPONSE.text))
else:
    print('Fetched no data!')