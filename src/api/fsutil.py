import os

from user import User, root_user
from node import getdb, get_node, get_dir_node


def initialized():
    return get_node('/').exist


def erase_everything():
    getdb().node.remove({})


def create_root_dir():
    node = get_dir_node('/')
    node._create(root_user)
    return node


def create_home_dir_for(user):
    node = get_home_dir(user)
    node.create(root_user)
    node.chown(root_user, user['username'])
    node.chgrp(root_user, user['username'])
    return node


def create_public_dir(path):
    node = get_dir_node(path).create(root_user)
    node.chmod(root_user, 0777)
    return node


def create_dir(user, path):
    path = os.path.join(get_home_dir(user).path, path)
    node = get_dir_node(path)
    node.create(user)
    return node


def get_home_dir(user):
    return get_dir_node('/home/' + user['username'])


def ls(operator, path):
    r = get_dir_node(path).list(operator)
    dirs = [d['path'] + '/' for d in r['dirs']]
    files = [f['path'] for f in r['files']]
    return dirs + files


if __name__ == '__main__':
    import json
    from node import get_node, getdb
    from test.setup import *
    from pprint import pprint
