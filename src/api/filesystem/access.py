import os

import util
from error import Error, PermissionDenied
from filesystem.node import get_by_path, Node, DirNode, FileNode


def get_node(visitor, path):
    return AccessControlledNode(visitor, path)


class AccessControlledNode(object):

    def __init__(self, visitor, path_or_node, silent=False):
        self.visitor = visitor
        if isinstance(path_or_node, Node):
            node = path_or_node
            path = node.path
        else:
            path = path_or_node
            node = get_by_path(path)
        self.path = path
        self.node = node
        self.silent = silent

    @property
    def exists(self):
        return self.node is not None

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
        return AccessControlledNode(self.visitor, self.node.parent_path)

    @property
    def children(self):
        return [AccessControlledNode(self.visitor, child)
                for child in self.node.children]

    def create_as_dir(self):
        parent = self.parent
        if not parent:
            parent.create_as_dir()
        if not parent.writable:
            raise PermissionDenied(self.path)
        self._create_as_dir()

    def get_meta(self):
        pass

    def list(self, depth):
        node = self.node
        # TODO: access control
        if not node.listable:
            raise Error(node.path + ' is not a directory')
        for child in self.children:
            pass

    def get_content_stream(self):
        node = self.node
        if not node.has_content:
            raise Error(node.path + ' is not file')

    def chmod(self, access):
        pass

    def _create_as_dir(self):
        meta = _make_meta(self.visitor.username, self.path)
        meta.update({
            'type': 'dir',
            'access': self.parent.access,
        })
        self.node = DirNode(meta)
        self.node.serialize()
        return self


def _make_meta(username, path):
    now = util.utc_now_str()
    return {
        'path': path,
        'name': os.path.basename(path),
        'parent_path': os.path.dirname(path),
        'owner': username,
        'group': username,
        'ctime': now,
        'mtime': now,
    }
