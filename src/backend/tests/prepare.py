import os
import json
from collections import OrderedDict

import requests

import conf
from user import User
from filesystem import get_node, fsutil
from filesystem.fsutil import *


root_user = User({'username': 'root'})
normal_user = User({'username': 'foo', 'groups': ['foo']})
guest_user = User({'username': ''})

user1 = User({'username': 'fans656', 'groups': ['f6']})
user2 = User({'username': 'tyn', 'groups': ['f6']})

origin = 'http://localhost:{}'.format(conf.port)


def print_node_meta(meta):
    del meta['_id']
    od = OrderedDict()
    def take(key):
        od[key] = meta[key]
    take('path')
    take('parent_path')
    take('type')
    take('name')
    take('owner')
    take('group')
    take('access')
    take('ctime')
    take('mtime')
    for key, val in meta.items():
        if key not in od:
            od[key] = val
    print json.dumps(od)


def init_storages():
    templates = store.storage.get_templates()
    storages = []
    for template in templates:
        storage = store.storage.get(None)
        storage.update(template)
        storages.append(storage)
    return storages


def init():
    fsutil.erase_everything()

    storages = init_storages()

    root_dir = fsutil.create_root_dir()
    root_dir.update_meta({
        'storage_ids': [s.meta['id'] for s in storages],
    })

    home1 = fsutil.create_home_dir_for(user1)
    home2 = fsutil.create_home_dir_for(user2)

    fsutil.create_dir_under_home(user1, 'img/girl')

    fsutil.create_public_dir('/public')
