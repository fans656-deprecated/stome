import os


class User(object):

    def __init__(self, meta):
        meta.update({
            'groups': meta.get('groups', []) + [meta['username']]
        })
        self.meta = meta

    @property
    def username(self):
        return self.meta['username']

    @property
    def groups(self):
        return self.meta['groups']

    @property
    def home_path(self):
        return os.path.join('/home', self.username)

    @property
    def is_root(self):
        return self.username == 'root'

    def own(self, node):
        if self.is_root:
            return True
        return node.owner == self.username

    def can_read(self, node):
        if self.is_root:
            return True
        if self.own(node) and node.owner_readable:
            return True
        if node.group in self.groups and node.group_readable:
            return True
        if node.other_readable:
            return True
        return False

    def can_write(self, node):
        if self.is_root:
            return True
        if self.own(node) and node.owner_writable:
            return True
        if node.group in self.groups and node.group_writable:
            return True
        if node.other_writable:
            return True
        return False

    def can_create(self, node):
        return self.can_write(node.parent)

    def can_remove(self, node):
        return self.can_write(node.parent)

    def __getitem__(self, key):
        return self.meta.__getitem__(key)

    def __repr__(self):
        return repr(self.meta)


root_user = User({'username': 'root'})
