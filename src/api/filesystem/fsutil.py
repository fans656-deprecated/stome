import db

from user import root_user
from filesystem.access import get_node


def initialized():
    return get_node(root_user, '/').exists


def erase_everything():
    db.getdb().node.remove()
    db.getdb().content.remove()
    db.getdb().storage.remove()
    db.getdb().instance.remove()


def create_root_dir():
    get_node(root_user, '/')._create_as_dir()


def create_public_dir(path):
    node = get_node(root_user, path)
    node.create_as_dir()
    node.chmod(root_user, 0777)
    return node


def create_home_dir_for(user):
    node = get_node(root_user, user.home_path)
    node.create_as_dir()
    username = user.username
    node.chown(username)
    node.chgrp(username)
    return node


def create_dir_under_home(user, path):
    node = get_node(user, user.home_path + path)
    node.create_as_dir()
    return node
