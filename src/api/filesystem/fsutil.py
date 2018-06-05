import os

import db
import util
import store
from user import root_user
from filesystem.access import get_node
from filesystem.node import make_node_by_meta


def initialized():
    return get_node(root_user, '/').exists


def initialize():
    create_root_dir()


def erase_everything():
    db.getdb().node.remove()
    db.getdb().storage.remove()
    db.getdb().content.remove()


def create_root_dir():
    now = util.utc_now_str()
    meta = {
        'type': 'dir',
        'path': '/',
        'name': '',
        'parent_path': '',
        'owner': 'root',
        'group': 'root',
        'ctime': now,
        'mtime': now,
        'access': 0775,
        'storage_ids': [],
        'size': 0,
    }
    make_node_by_meta(meta)
    return get_node(root_user, '/')


def create_public_dir(path):
    node = get_node(root_user, path)
    node.create_as_dir()
    node.chmod(0777)
    return node


def create_home_dir_for(user):
    node = get_node(root_user, user.home_path)
    node.create_as_dir()
    username = user.username
    node.chown(username)
    node.chgrp(username)
    return node


def create_dir_under_home(user, path):
    node = get_node(user, os.path.join(user.home_path, path))
    node.create_as_dir()
    return node
