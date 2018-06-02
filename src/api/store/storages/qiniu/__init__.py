import os
import json

import store


keys_fpath = os.path.expanduser('~/.qiniu/keys.json')
if os.path.exists(keys_fpath):
    with open(keys_fpath) as f:
        keys = json.load(f)
    access_key = keys['access-key']
    secret_key = keys['secret-key']
else:
    access_key = '<your-access-key>'
    secret_key = '<your-secret-key>'


template = {
    'type': 'qiniu',
    'name': 'qiniu',
    'domain': 'http://res-eno-zone.5awo.com/',
    'access-key': access_key,
    'secret-key': secret_key,
}


class StorageInstanceQiniu(store.instance.Instance):

    def init(self):
        self.update_meta({
            'foo': 'bar',
        })

Instance = StorageInstanceQiniu
