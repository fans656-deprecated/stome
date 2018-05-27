import os
import time
import json
from pprint import pprint
from collections import OrderedDict

import requests
import jwt

import conf
import util
from db import getdb
from node import get_node
from test.setup import *
from store import *
import store


origin = 'http://localhost:{}'.format(conf.port)


def upload_file():
    class Stream(object):

        def __init__(self, s):
            self.s = s
            self.i = 0

        def read(self, n):
            i = self.i
            r = self.s[i:i+n]
            self.i = i + n
            return r

    data = 'hello stome\n'
    md5 = util.calc_md5(data)

    r = requests.put(origin + '/t.txt', params={
        'md5': md5,
        'size': len(data),
    }, data=data)


def list_dir():
    r = requests.get(origin + '?depth=1')
    print json.dumps(r.json(), indent=2)


def get_storage_templates():
    r = requests.get(origin + '?storage-templates')
    print json.dumps(r.json(), indent=2)


def get_storages():
    r = requests.get(origin + '?storage')
    print json.dumps(r.json(), indent=2)


def put_storage(storage):
    r = requests.put(origin + '?storage', json=storage)
    return json.dumps(r.json(), indent=2)


init()

#upload_file()
#
#time.sleep(0.1)
#node = get_node('/t.txt')
#print node.content
#print
#for ins in node.content.instances:
#    print ins
