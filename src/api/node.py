import os
import json
from collections import OrderedDict

import util
from db import getdb
from errors import *


def get_existed_node(path):
    node = get_node(path)
    if not node.exist:
        raise NotFound
    return node


def get_node(path):
    return Node(util.normalized_path(path))


def get_file_node(path):
    node = get_node(path)
    node.type = 'file'
    return node


def get_dir_node(path):
    node = get_node(path)
    if node.exist and not node.is_dir:
        raise NotDir(node)
    node.type = 'dir'
    return node


class Node(object):

    def __init__(self, path, meta=None):
        if not meta:
            meta = getdb().node.find_one({'path': path}, {'_id': False})
        if meta:
            self.meta = meta
            self.exist = True
        else:
            self.meta = {
                'name': os.path.basename(path),
                'parent': get_parent_path(path),
            }
            self.exist = False
        self.meta['path'] = path

    @property
    def path(self):
        return self.meta['path']

    @property
    def name(self):
        return self.meta['name']

    @property
    def type(self):
        return self.meta['type']

    @type.setter
    def type(self, type):
        self.meta['type'] = type

    @property
    def is_dir(self):
        return self.type == 'dir'

    @property
    def is_file(self):
        return self.type == 'file'

    @property
    def parent(self):
        return get_dir_node(self.meta['parent'])

    @property
    def owner(self):
        return self.meta['owner']

    @property
    def group(self):
        return self.meta['group']

    @property
    def access(self):
        return self.meta['access']

    @property
    def size(self):
        return self.meta['size']

    @property
    def owner_readable(self):
        return bool(self.access & 0600)

    @property
    def owner_writable(self):
        return bool(self.access & 0200)

    @property
    def group_readable(self):
        return bool(self.access & 0060)

    @property
    def group_writable(self):
        return bool(self.access & 0020)

    @property
    def other_readable(self):
        return bool(self.access & 0006)

    @property
    def other_writable(self):
        return bool(self.access & 0002)

    @property
    def children(self):
        metas = getdb().node.find({'parent': self.path}, {'_id': False})
        return [Node(m['path'], m) for m in metas]

    @property
    def as_ls_entry(self):
        r = dict(self.meta)
        r.update({
            'listable': self.is_dir,
        })
        return r

    def create(self, user, meta=None):
        if self.exist:
            raise Existed(self)
        parent = self.parent
        if not parent.exist:
            self.parent.create(user, meta)
        return self._create(user, meta)

    def list(self, user, depth):
        if not user.can_read(self):
            raise CantRead(self)
        return list_directory(self, depth)

    def chown(self, operator, username):
        return self.update_meta(operator, {'owner': username})

    def chgrp(self, operator, group):
        return self.update_meta(operator, {'group': group})

    def chmod(self, operator, mod):
        return self.update_meta(operator, {'access': mod})

    def get_meta(self, user):
        if not self.exist:
            raise NotFound(self)
        if not user.can_read(self):
            raise CantRead(self)
        return self.meta

    def update_meta(self, operator, meta, silent=False):
        if not meta:
            return
        if operator.own(self):
            self._serialize(update=meta)
        elif not silent:
            raise CantWrite(self)
        return self

    def move(self, user, dst):
        if not user.can_remove(self):
            raise CantMove(self)
        dst.clone(self)
        src.remove()

    def clone(self, user, src, silent=False):
        try:
            if self.exist:
                raise AlreadyExist(dst)
            if not src.exist:
                raise NotFound(src)
            if not user.can_write(dst.parent):
                raise CantWrite(dst)
            self.create(user, src.meta)
            if src.is_dir and user.can_read(src):
                for child in src.children:
                    dst = get_node(self.path + '/' + child.name)
                    dst._clone(user, child_src)
            return True
        except Exception as e:
            if not silent:
                raise e
            return False

    def remove(self, operator, recursive=False, silent=False):
        if not self.exist:
            if silent:
                return
            else:
                raise NotExist(self)
        parent = self.parent
        if not operator.can_write(parent):
            if silent:
                return
            else:
                raise CantRemove(self)
        if self.is_file:
            self._remove_single()
        elif self.is_dir:
            if not recursive:
                if silent:
                    return
                else:
                    raise IsDir(self)
            for child in self.children:
                child.remove(operator, recursive, silent)
            self._remove()

    def iter_content(self, visitor):
        if not visitor.can_read(self):
            raise CantRead(self)
        return 'todo'

    def _remove(self):
        getdb().node.remove({'path': self.path})

    def _create(self, user, meta=None):
        username = user.username
        now = util.utc_now_str()
        self.meta.update({
            'owner': username,
            'group': username,
            'ctime': now,
            'mtime': now,
            'size': 0,
            'storages': [],
        })
        if self.is_dir:
            self.meta.update({
                'access': 0775,
            })
        else:
            self.meta.update({
                'access': 0664,
            })
        self.meta.update(meta or {})
        if not user.can_create(self):
            raise CantCreate(self)
        self.exist = True
        self._serialize(update=self.meta, upsert=True)
        return self

    def _serialize(self, update=None, upsert=False):
        self.meta.update(update or {})
        getdb().node.update({'path': self.path}, self.meta, upsert=upsert)

    def __repr__(self):
        return repr(self.meta)

    def __str__(self):
        meta = dict(self.meta)
        if 'access' in meta:
            meta['access'] = '0{:03o}'.format(meta['access'])

        def take(field):
            d[field] = meta.get(field, '???')

        d = OrderedDict()
        take('path')
        take('type')
        take('owner')
        take('group')
        take('access')
        take('name')
        take('parent')
        take('ctime')
        take('mtime')
        for k, v in meta.items():
            if k not in d:
                d[k] = v
        return 'Node({})'.format(json.dumps(d, indent=2))


def get_parent_path(path):
    if path == '/':
        return ''
    path = '/'.join(path.split('/')[:-1])
    if not path.startswith('/'):
        path = '/' + path
    return path


def list_directory(node, depth):
    dirs = []
    files = []
    for child in node.children:
        if child.is_dir:
            dirs.append(get_list_result(child, depth - 1))
        elif child.is_file:
            files.append(get_list_result(child.as_ls_entry, depth - 1))
    res = node.as_ls_entry
    res.update({
        'dirs': dirs,
        'files': files,
    })
    return res


def get_list_result(node, depth):
    if depth:
        return list_directory(node, depth)
    else:
        return node.as_ls_entry


if __name__ == '__main__':
    print get_parent_path('/')
    print get_parent_path('/foo')
    print get_parent_path('/foo/bar')
    exit()

    getdb().node.remove({})

    user_root = {'username': 'root'}
    user_owner = {'username': 'foo'}
    user_group = {'username': 'bar', 'groups': ['foo']}
    user_other = {'username': 'baz'}

    root = Node('/')
    home = Node('/home/' + user_owner['username'])

    print home.writable_by(user_group)
