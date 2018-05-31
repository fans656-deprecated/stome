import os
import json
from collections import OrderedDict

import db
import util
import store
from errors import *


def get_existed_node(path):
    node = get_node(path)
    if not node.exists:
        raise Error('{} not exists'.format(path), 404)
    return node


def get_dir_or_file_node(path):
    if path.endswith('/'):
        return get_dir_node(path)
    else:
        return get_file_node(path)


def get_dir_node(path):
    node = get_node(path)
    if node.exists and not node.is_dir:
        raise NotDir(node)
    node.type = 'dir'
    return node


def get_file_node(path):
    node = get_node(path)
    if node.exists and not node.is_file:
        raise NotFile(node)
    node.type = 'file'
    return node


def get_node(path):
    return Node(util.normalized_path(path))


class Node(object):

    def __init__(self, path, meta=None):
        if not meta:
            meta = db.getdb().node.find_one({'path': path}, {'_id': False})
        if meta:
            self.meta = meta
            self.exists = True
        else:
            self.meta = {
                'name': os.path.basename(path),
                'parent': get_parent_path(path),
            }
            self.exists = False
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

    @property
    def mimetype(self):
        return self.meta['mimetype']

    @type.setter
    def type(self, type):
        self.meta['type'] = type

    @property
    def is_dir(self):
        return self.type == 'dir'

    @property
    def is_root(self):
        return self.path == '/'

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

    @size.setter
    def size(self, size):
        self._serialize({'size': size})

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
        metas = db.getdb().node.find({'parent': self.path}, {'_id': False})
        return [Node(m['path'], m) for m in metas]

    @property
    def md5(self):
        return self.meta['md5']

    @property
    def as_ls_entry(self):
        meta = self.inherited_meta
        meta.update({
            'listable': self.is_dir,
        })
        return meta

    @property
    def storage_ids(self):
        return self.meta.get('storage_ids') or self.parent.storage_ids

    @property
    def content(self):
        return store.content.get(self.md5)

    @property
    def inherited_meta(self):
        meta = dict(self.meta)
        meta.update({
            'storage_ids': self.storage_ids,
        })
        return meta

    def create(self, user, meta=None):
        if self.exists:
            raise Existed(self)
        parent = self.parent
        if not parent:
            self.parent.create(user, meta)
        if not user.can_create(self):
            raise CantCreate(self)
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
        if not self.exists:
            raise NotFound(self)
        if not user.can_read(self):
            raise CantRead(self)
        return self.inherited_meta

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
            if self.exists:
                raise AlreadyExist(dst)
            if not src.exists:
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
        if not self.exists:
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
            self._remove_single()

    def iter_content(self, visitor):
        if not visitor.can_read(self):
            raise CantRead(self)
        return self.content.iter()

    def _inc_size(self, size):
        self.size += size
        if not self.is_root:
            self.parent._inc_size(size)

    def _remove_single(self):
        db.getdb().node.remove({'path': self.path})
        self._inc_size(-self.size)

    def _create(self, user, meta):
        node_type = meta.get('type')
        if node_type is None:
            raise Error('node creation need to specify type')
        if node_type == 'dir':
            size = 0
        elif node_type == 'file':
            size = meta.get('size')
        else:
            raise Error('node type {} is not supported'.format(node_type))
        username = user.username
        now = util.utc_now_str()

        self.meta.update({
            'type': node_type,
            'owner': username,
            'group': username,
            'ctime': now,
            'mtime': now,
            'size': size,
        })
        if self.is_dir:
            self.meta.update({
                'access': 0775,
            })
        elif self.is_file:
            self.meta.update({
                'access': 0664,
                'md5': md5,
                'mimetype': mimetype or 'application/octet-stream'
            })
            self._add_instances()
        self.meta.update(meta or {})
        self.exists = True
        self._serialize(update=self.meta, upsert=True)
        self.parent._inc_size(size)
        return self

    def _add_instances(self):
        content = self.content
        if not content.exists:
            content.create(self.size)
        for storage_id in self.storage_ids:
            content.add_instance(storage_id)

    def _serialize(self, update=None, upsert=False):
        self.meta.update(update or {})
        db.getdb().node.update({'path': self.path}, self.meta, upsert=upsert)

    def __nonzero__(self):
        return self.exists

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
            files.append(child.as_ls_entry)
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


class Node(object):
    """
    Represent basic info of a file system entity (e.g. file/directory)

    Have the following fields:

        path (unicode) - The entity's absolute path, e.g. '/img/girl/blue.jpg'
        name (unicode) - The entity's name, e.g. 'blue.jpg'
        parent_path (unicode) - The entity's parent's absolute path, e.g. '/img/girl'
        owner (unicode) - Owner's username, e.g. 'fans656'
        group (unicode) - Group name, e.g. 'fans656'
        access (int) - Access control like Linux, e.g. 0775 => rwxrwxr-x
        ctime (str) - Creation time, e.g. '2018-05-31 09:55:32 UTC'
        mtime (str) - Modificaiton time, e.g. '2018-05-31 09:55:32 UTC'

    Note:

        Root path '/' has a parent path of itself, i.e. '/'
    """

    def __init__(self, path):
        meta = db.getdb().node.find_one({'path': path}, {'_id': False})
        if meta:
            self._meta = meta
            self._exists = True
        else:
            self._meta = {
                'path': path,
                'name': os.path.basename(path),
                'parent': get_parent_path(path),
            }
            self._exists = False

    @property
    def path(self):
        return self._meta['path']

    @property
    def name(self):
        return self._meta['name']

    @property
    def parent_path(self):
        return self._meta['parent_path']

    @property
    def parent(self):
        return get_existed_node(self._parent_path)

    @property
    def exists(self):
        return self._exists

    def create(self):
        self._serialize()

    def _serialize(self):
        db.getdb().node.update({'path': self.path}, self._meta, upsert=True)

    def __nonzero__(self):
        return self.exists


class DirNode(Node):

    def __init__(self, path):
        super(DirNode, path)
        if not self:
            self._meta.update({
                'type': 'dir',
                'size': 0,
            })


class FileNode(object):

    def __init__(self, path):
        super(FileNode, path)
        if not self:
            self._meta.update({
                'type': 'file',
            })

    @property
    def content(self):
        return store.content.get(md5)

    def create(self, size, md5, mimetype):
        self._meta.update({
            'size': size,
            'md5': md5,
            'mimetype': mimetype,
        })
        content = self.content
        for storage in self.parent.storages:
            content.add_storage(storage)
        super(FileNode, self).create()


class LinkNode(object):

    def __init__(self, path, target_node):
        super(LinkNode, path)
        if not self:
            self._update_meta({
                'type': 'link',
                'size': 0,
                'target_path': target_node.path,
            })
