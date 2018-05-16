"""
Node repr:

    {
        'path': '/img/girl',
        'type': 'dir',  # dir/file
        'owner': 'fans656',
        'group': 'fans656',
        'access': 0775,
        'parent': '/img',
        'ctime': '2018-05-12 23:24:01 UTC',
        'mtime': '2018-05-14 09:18:22 UTC',
    }

dir extras:

    {
        'total-size': 2351348,
        'descendant-mtime': '2018-05-17 14:25:07 UTC',
    }

file extras:

    {
        'storage': [
            {
                'type': 'local',
                'path': '/home/fans656/test.jpg',
            },
            {
                'type': 'qiniu',
                'url': 'http://p7a4nj2zt.bkt.clouddn.com/blue.jpg',
                'encryption': 'simple',
            }
        ],
    }
"""
import json

import pymongo

import util


def get_node(path):
    path = util.normalized_path(path)
    return Node(path)


class Node(object):

    def __init__(self, path):
        meta = getdb().node.find_one({'path': path})
        if meta:
            self.meta = meta
            self.exist = True
        else:
            self.meta = {}
            self.exist = False
        self.meta['path'] = path

    @property
    def isdir(self):
        return self.meta['isdir']

    @property
    def isfile(self):
        return not self.isdir

    @property
    def parent(self):
        return Node(self.meta['parent'])

    @property
    def access(self):
        return self.meta['access']

    @property
    def owner(self):
        return self.meta['owner']

    @property
    def group(self):
        return self.meta['group']

    @property
    def owner_readable(self):
        return bool(self.access & 0600)

    @property
    def owner_writable(self):
        return bool(self.access & 0400)

    @property
    def group_readable(self):
        return bool(self.access & 0060)

    @property
    def group_writable(self):
        return bool(self.access & 0040)

    @property
    def other_readable(self):
        return bool(self.access & 0006)

    @property
    def other_writable(self):
        return bool(self.access & 0004)

    def readable_by(self, user):
        if user.isroot:
            return True
        if user.own(self) and self.owner_readable:
            return True
        if user.in_group(self.group) and self.group_readable:
            return True
        if self.other_readable:
            return True
        return False

    def writable_by(self, user):
        if user.isroot:
            return True
        if self.own_by(user) and self.owner_writable:
            return True
        if user.in_group(self.group) and self.group_writable:
            return True
        if self.other_writable:
            return True
        return False

    def own_by(self, user):
        return self.owner == user.username

    def create(self, meta, user):
        username = user['username']
        now = util.utc_now_str()
        self.meta.update({
            'owner': username,
            'group': username,
            'parent': get_parent_path(self.meta['path']),
            'ctime': now,
            'mtime': now,
        })

    def save(self):
        meta = self.meta
        print json.dumps(meta, indent=2)

    def __repr__(self):
        return json.dumps({
            'path': self.path,
            'access': '{:03o}'.format(self.access),
        })


class FileNode(Node):

    def create(self, meta, user):
        super(DirNode, self).create(meta, user)
        self.meta.update({
            'type': 'file',
            'access': 0664,
            'storage': [],
        })


class DirNode(Node):

    @property
    def children(self):
        pass

    def create(self, meta, user):
        super(DirNode, self).create(meta, user)
        self.meta.update({
            'type': 'dir',
            'access': 0775,
            'total_size': 0,
            'descendant_mtime': self.meta['mtime'],
        })


def user_own_node(user, node):
    if is_root_user(user):
        return True
    if user['username'] == node.owner:
        return True
    return False


def user_in_group(user, group):
    if group == user['username']:
        return True
    if group in user.get('groups', []):
        return True
    return False


def is_root_user(user):
    return user['username'] == 'root'


def create_root_directory():
    Node('/', meta={
        'path': '/',
        'owner': 'root',
        'group': 'root',
        'access': 032,
        'isdir': True,
    }).save()


def create_user_home_directory(user):
    username = user['username']
    Node('/home/' + username, meta={
        'owner': username,
        'group': username,
        'access': 032,
        'isdir': True,
    }).save()


def getdb(g={}):
    if 'db' not in g:
        g['db'] = pymongo.MongoClient().stome
    return g['db']


def get_parent_path(path):
    parts = path.split('/')
    parts.pop()
    path = '/'.join(parts)
    if not path.startswith('/'):
        path = '/' + path
    return path


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
