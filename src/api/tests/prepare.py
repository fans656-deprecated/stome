import os

from user import User

from filesystem import get_node, fsutil


root_user = User({'username': 'root'})
normal_user = User({'username': 'foo', 'groups': ['foo']})
guest_user = User({'username': ''})

user1 = User({'username': 'fans656', 'groups': ['f6']})
user2 = User({'username': 'tyn', 'groups': ['f6']})


#def init_storages():
#    templates = store.storage.get_templates()
#    storages = []
#    for template in templates:
#        if template['type'] == 'local':
#            storage = store.storage.get(None)
#            storage.update(template)
#            storages.append(storage)
#            break
#    return storages


def init():
    fsutil.erase_everything()

    #storages = init_storages()

    root_dir = fsutil.create_root_dir()
    #root_dir.update_meta(root_user, {
    #    'storage_ids': [s.meta['id'] for s in storages],
    #})

    public_dir = fsutil.create_public_dir('/public')

    home1 = fsutil.create_home_dir_for(user1)
    home2 = fsutil.create_home_dir_for(user2)

    fsutil.create_dir_under_home(user1, 'img/girl')
