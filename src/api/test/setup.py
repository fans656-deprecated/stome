import os

import fsutil
import store
from user import User
from node import get_node, get_dir_node, get_file_node


root_user = User({'username': 'root'})
user1 = User({'username': 'fans656', 'groups': ['f6']})
user2 = User({'username': 'tyn', 'groups': ['f6']})
guest_user = User({'username': ''})


def init_storages():
    templates = store.storage.get_templates()
    storages = []
    for template in templates:
        if template['type'] == 'local':
            storage = store.storage.get(None)
            storage.update(template)
            storages.append(storage)
            break
    return storages


def init():
    os.system('rm ~/.stome-files/* 2> /dev/null')
    os.system('rm ../../files/transfer/* 2> /dev/null')
    fsutil.erase_everything()

    storages = init_storages()

    root_dir = fsutil.create_root_dir()
    root_dir.update_meta(root_user, {
        'storage_ids': [s.meta['id'] for s in storages],
    })

    home1 = fsutil.create_home_dir_for(user1)
    home2 = fsutil.create_home_dir_for(user2)

    fsutil.create_dir(user1, 'img/girl')

    public_dir = fsutil.create_public_dir('/public')
