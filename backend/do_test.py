import json
from pprint import pprint

import requests

from node import get_node
#from test import setup
#from test import test_user

origin = 'http://localhost:6001'
r = requests.get(origin + '/')
print r.text
