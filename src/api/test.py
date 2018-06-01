import os
import time
import json

import requests
import jwt

import db
import conf
import util
import filesystem

import tests


origin = 'http://localhost:{}'.format(conf.port)


def do_test():
    # HEAD resource existance
    assert requests.head(origin).status_code == 200
    assert requests.head(origin + '/').status_code == 200
    assert requests.head(origin + '/home').status_code == 200
    assert requests.head(origin + '/home/').status_code == 200
    assert requests.head(origin + '/asdfasfd').status_code == 404
    assert requests.head(origin + '/asdfasfd/').status_code == 404


def list_dir():
    r = requests.get(origin + '?depth=1')
    print json.dumps(r.json(), indent=2)


def get_meta(path):
    r = requests.get(origin + path + '?meta')
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


tests.test_filesystem.test_fsutil.run()
