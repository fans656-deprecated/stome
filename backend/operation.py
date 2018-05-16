import os
import datetime

from node import Node, FileNode, DirNode, get_node
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
    node = DirNode(path)
    node.create(meta, user)
    node.save()


def ls(path, user=None):
    user = user or GuestUser
    node = DirNode(path)
    if not node.exist:
        raise NotFound(path)
    if not node.is_dir:
        raise NotDir(path)
    if not node.parent.readable_by(user):
        raise CantRead(path)
    dirs = []
    files = []
    for child in node.children:
        if child.is_dir:
            dirs.append(make_ls_entry(child))
        elif child.is_file:
            files.append(make_ls_entry(child))
    return {
        'dirs': dirs,
        'files': files,
    }


def mv(src_path, dst_path, user=None):
    src = get_node(src_path)
    if not src.exist:
        raise NotFound(src_path)
    if '/' not in dst_path:
        dst_path = os.path.join(src.parent.path, dst_path)
    dst = get_node(dst_path)
    if dst.exist and dst.is_dir:
        raise DirExisted(dst_path)


def cp(src_path, dst_path, user=None):
    pass


def rm(path, user=None):
    pass


def get_meta(path, query=None, user=None):
    pass


def update_meta(path, meta, user=None):
    pass


class OperationError(Exception):

    def __init__(self, path):
        self.path = path


class NotFound(OperationError): pass
class NotDir(OperationError): pass
class CantRead(OperationError): pass
class DirExisted(OperationError): pass


GuestUser = User({'username': 'guest'})


if __name__ == '__main__':
    #mkdir('/img')
    #download('/img')
    mv('/img', 'image')
