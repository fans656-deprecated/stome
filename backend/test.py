import os

import jwt
import requests

import conf


home = os.path.expanduser('~')
prikey = open(os.path.join(home, '.ssh/id_rsa')).read().strip()
user = {
    'username': 'fans656 fan',
}
token = jwt.encode(user, prikey, algorithm='RS512')

import base64
def decode(s):
    return base64.urlsafe_b64decode(s + b'=' * (4 - (len(s) % 4 or 4)))

header, payload, signature = token.split('.')
print decode(header)
print decode(payload)
print signature
exit()

origin = 'http://localhost:{}'.format(conf.port)

r = requests.get(origin, headers={
    'Authorization': 'Bearer ' + token
})
print r.text
exit()


#r = requests.get(origin + '/', json={'token': token})
#print r.json()

#r = requests.put(origin + '/img', json={'token': token})
r = requests.put(origin + '/img')
print r.text
#print r.json()
