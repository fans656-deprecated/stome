import db


def get_node_by_path(path):
    meta = db.getdb().node.find_one({'path': path}, {'_id': False})
    if not meta:
        return None
    node_type = meta['type']
    if node_type == 'file':
        return FileNode(meta)
    elif node_type == 'dir':
        return DirNode(meta)
    elif node_type == 'link':
        return LinkNode(meta)
    else:
        assert 0, 'unsupported type {}'.format(node_type)


def make_node_by_meta(meta):
    node_type = meta['type']
    if node_type == 'dir':
        node = DirNode(meta)
    elif node_type == 'file':
        node = FileNode(meta)
    elif node_type == 'link':
        node = LinkNode(meta)
    else:
        raise TypeError('unrecognized node type: ' + node_type)
    if node.size:
        node.parent.size += node.size
    node.serialize()
    return node


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
    """

    def __init__(self, meta):
        self._meta = meta

    @property
    def meta(self):
        meta = dict(self._meta)
        meta.update({
            'listable': self.listable,
            'storage_ids': self.storage_ids,
        })
        return meta

    @property
    def size(self):
        return self._meta['size']

    @size.setter
    def size(self, new_size):
        parent = self.parent
        if parent:
            parent.size += new_size - self.size
        self.update_meta({'size': new_size})

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
    def owner(self):
        return self._meta['owner']

    @property
    def group(self):
        return self._meta['group']

    @property
    def access(self):
        return self._meta['access']

    @property
    def ctime(self):
        return self._meta['ctime']

    @property
    def mtime(self):
        return self._meta['mtime']

    @property
    def storage_ids(self):
        ret = self._meta.get('storage_ids')
        if not ret:
            ret = self.parent.storage_ids
        return ret

    @property
    def parent(self):
        return get_node_by_path(self.parent_path)

    @property
    def listable(self):
        return False

    @property
    def has_content(self):
        return False

    def delete(self):
        self.parent.size -= self.size
        db.getdb().node.remove({'path': self.path})

    def chmod(self, access):
        self.update_meta({'access': access})

    def chown(self, username):
        self.update_meta({'owner': username})

    def chgrp(self, groupname):
        self.update_meta({'group': groupname})

    def update_meta(self, meta):
        self._meta.update(meta)
        self.serialize()

    def serialize(self):
        db.getdb().node.update({'path': self.path}, self._meta, upsert=True)


class DirNode(Node):

    def __init__(self, meta):
        super(DirNode, self).__init__(meta)

    @property
    def listable(self):
        return True

    @property
    def children(self):
        r = db.getdb().node.find({'parent_path': self.path}, {'path': 1, '_id': 0})
        child_paths = [c['path'] for c in r]
        return map(get_node_by_path, child_paths)


class RootNode(DirNode):

    @property
    def parent(self):
        return self


class FileNode(Node):

    def __init__(self, meta):
        super(FileNode, self).__init__(meta)
        if not self:
            self._meta.update({
                'type': 'file',
            })

    @property
    def has_content(self):
        return True

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


class LinkNode(Node):

    def __init__(self, meta):
        super(LinkNode, meta)
        self.target_node = get_node_by_path(meta['target_path'])

    @property
    def listable(self):
        return self.target_node.listable

    @property
    def has_content(self):
        return self.target_node.has_content
