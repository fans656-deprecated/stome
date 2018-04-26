import sys; sys.path.append('..')

import requests
import jwt

import conf
import util


prikey = open('/home/fans656/.ssh/id_rsa').read().strip()
pubkey = open('/home/fans656/.ssh/id_rsa.pub').read().strip()
headers = {
    'Authorization': 'Bearer ' + jwt.encode({'pubkey': pubkey}, prikey, 'RS512')
}
origin = 'http://localhost:{}'.format(conf.port)

#print requests.get(origin, headers=headers).text

data = open('../errors.py').read()
md5 = util.calc_md5(data)
print requests.put(origin + '/' + md5, headers=headers, files={'data': data}).text
