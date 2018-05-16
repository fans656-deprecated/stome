import datetime

from node import Node, FileNode, DirNode
from user import User


def upload(path, meta, data, user=None):
    pass


def download(path, user=None):
    node = Node(path)
    if not node.exist:
        raise NotFound(path)
    return node.iter_content()


def mkdir(path, meta=None, user=None):
    meta = meta or {}
    user = user or GuestUser
    node = DirNode(normalized_path(path))
    node.create(meta, user)
    node.save()


def ls(path, user=None):
    pass


def mv(path, name, user=None):
    pass


def cp(src_path, dst_path, user=None):
    pass


def rm(path, user=None):
    pass


def get_meta(path, query=None, user=None):
    pass


def update_meta(path, meta, user=None):
    pass


def normalized_path(path):
    parts = []
    for part in path.split('/'):
        if not part or part == '.':
            continue
        elif part == '..':
            if parts:
                parts.pop()
        else:
            parts.append(part)
    path = '/'.join(parts)
    if not path.startswith('/'):
        path = '/' + path
    return path


class NotFound(Exception):

    def __init__(self, path):
        self.path = path


GuestUser = User({'username': 'guest'})


if __name__ == '__main__':
    mkdir('/img')
    #download('/img')
