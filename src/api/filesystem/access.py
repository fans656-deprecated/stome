import os

import util
from error import Error, PermissionDenied, Conflict
from filesystem.node import get_node_by_path, make_node_by_meta, Node


def get_node(visitor, path):
    path = util.normalized_path(path)
    return AccessControlledNode(visitor, path)


class AccessControlledNode(object):
    """
    Properties:

        + exists
        + readable
        + writable
        + executable
        + owned
        + parent
        + children

    Operations:

        + create_as_dir
        + create_as_file
        + create_as_link
        + get_meta
        + list
        + get_content_stream
        + chmod
        + chown
        + chgrp
    """

    def __init__(self, visitor, path_or_node):
        self.visitor = visitor
        if isinstance(path_or_node, Node):
            node = path_or_node
            path = node.path
        else:
            path = path_or_node
            node = get_node_by_path(path)
        self.path = path
        self.node = node

    @property
    def exists(self):
        return self.node is not None

    @property
    def listable(self):
        return self.readable and self.node and self.node.listable

    @property
    def readable(self):
        visitor = self.visitor
        if visitor.is_root:
            return True
        if visitor.own(self.node) and self.owner_readable:
            return True
        if node.group in visitor.groups and self.group_readable:
            return True
        if self.other_readable:
            return True
        return False

    @property
    def writable(self):
        visitor = self.visitor
        if visitor.is_root:
            return True
        if visitor.own(self.node) and self.owner_writable:
            return True
        if node.group in visitor.groups and self.group_writable:
            return True
        if self.other_writable:
            return True
        return False

    @property
    def executable(self):
        visitor = self.visitor
        if visitor.is_root:
            return True
        if visitor.own(self.node) and self.owner_executable:
            return True
        if node.group in visitor.groups and self.group_executable:
            return True
        if self.other_executable:
            return True
        return False

    @property
    def owned(self):
        visitor = self.visitor
        return visitor.is_root or self.node.owner == visitor.username

    @property
    def owner_readable(self):
        return self.node.access & 0400

    @property
    def owner_writable(self):
        return self.node.access & 0200

    @property
    def owner_executable(self):
        return self.node.access & 0100

    @property
    def group_readable(self):
        return self.node.access & 0040

    @property
    def group_writable(self):
        return self.node.access & 0020

    @property
    def group_executable(self):
        return self.node.access & 0010

    @property
    def other_readable(self):
        return self.node.access & 0004

    @property
    def other_writable(self):
        return self.node.access & 0002

    @property
    def other_executable(self):
        return self.node.access & 0001

    @property
    def parent(self):
        parent_path = self.node.parent_path if self.node else os.path.dirname(self.path)
        return AccessControlledNode(self.visitor, parent_path)

    @property
    def children(self):
        nodes = [
            AccessControlledNode(self.visitor, child)
            for child in self.node.children
        ]
        return filter(bool, nodes)

    @property
    def subdirs(self):
        return [c for c in self.children if c.listable]

    @property
    def files(self):
        return [c for c in self.children if not c.listable]

    @property
    def meta(self):
        return self.node.meta

    def create_as_dir(self):
        self._prepare_node_creation()
        self._create_as_dir()

    def create_as_file(self, size, md5, mimetype):
        self._prepare_node_creation()
        self._create_as_file(size, md5, mimetype)

    def delete(self):
        if not self:
            raise NotFound(self.path)
        parent = self.parent
        if not parent or not parent.writable:  # bool(root.parent) == False
            raise PermissionDenied(self.path)
        self._delete()

    def list(self, depth):
        if not self.readable:
            return None
        meta = self.node.meta
        if self.listable and depth:
            meta.update({
                'dirs': [d.list(depth - 1) for d in self.subdirs],
                'files': [f.node.meta for f in self.files],
            })
        return meta

    def get_content_stream(self):
        node = self.node
        if not node.has_content:
            raise ResourceError('Not file', self.path)

    def update_meta(self, meta):
        # TODO: access control
        self.node.update_meta(meta)

    def chmod(self, access):
        if not self.owned:
            raise PermissionDenied(self.path)
        self.node.chmod(access)

    def chown(self, username):
        if not self.owned:
            raise PermissionDenied(self.path)
        self.node.chown(username)

    def chgrp(self, groupname):
        if not self.owned:
            raise PermissionDenied(self.path)
        self.node.chgrp(groupname)

    def _delete(self):
        print 'AccessControlledNode._delete', self, self.node
        self.node.delete()

    def _create_as_dir(self):
        meta = self._make_meta()
        meta.update({
            'type': 'dir',
            'size': 0,
        })
        self.node = make_node_by_meta(meta)
        return self

    def _create_as_file(self, size, md5, mimetype):
        meta = self._make_meta()
        meta.update({
            'type': 'file',
            'size': size,
            'md5': md5,
            'mimetype': mimetype,
            'status': 'init',
            'storage_ids': [],
        })
        self.node = make_node_by_meta(meta)
        for storage_id in self.parent.node.storage_ids:
            self.node.add_content(storage_id)
        return self

    def _prepare_node_creation(self):
        if self.exists:
            raise Conflict(self.path)
        parent = self.parent
        if not parent:
            parent.create_as_dir()
        return parent

    def _make_meta(self):
        path = self.path
        username = self.visitor.username
        now = util.utc_now_str()
        parent = self.parent
        return {
            'path': path,
            'name': os.path.basename(path),
            'parent_path': os.path.dirname(path),
            'owner': username,
            'group': username,
            'ctime': now,
            'mtime': now,
            'access': parent.node.access,
        }

    def __nonzero__(self):
        return self.exists

    def __repr__(self):
        return 'ANode{{{}}}'.format(self.path)
