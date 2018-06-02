import os

import db
import conf
import store


def get(storage_id, md5):
    meta = db.getdb().instance.find_one({
        'storage_id': storage_id,
        'md5': md5,
    }, {'_id': False})
    Instance = get_class(store.storage.get(storage_id).type)
    if meta:
        return Instance(meta)
    else:
        instance = Instance(None)
        instance.meta.update({
            'storage_id': storage_id,
            'md5': md5,
        })
        return instance


def get_by_name(name):
    meta = db.getdb().instance.find_one({'name': name}, {'_id': False})
    return Storage(meta)


def get_class(type):
    return getattr(store.storages, type).Instance


class Instance(object):

    def __init__(self, meta):
        if meta:
            self.meta = meta
            self.exists = True
        else:
            self.meta = {}
            self.exists = False

    @property
    def done(self):
        return self.meta['status'] == 'done'

    @property
    def storage_id(self):
        return self.meta['storage_id']

    @property
    def storage(self):
        return store.storage.get(self.storage_id)

    @property
    def md5(self):
        return self.meta['md5']

    @property
    def key(self):
        return self.storage_id + '-' + self.md5

    @property
    def ref_count(self):
        return self.meta['ref_count']

    @ref_count.setter
    def ref_count(self, count):
        if count == 0:
            self.delete()
        else:
            self.update_meta({'ref_count': count})

    def query(self, request):
        return  # no-op

    def iter_content(self):
        return self.iter()

    def iter(self):
        yield 'TODO ' + self._classname

    def create(self):
        self.update_meta({
            'status': 'init',
            'ref_count': 0,
        })
        self.init()
        return self

    def update_meta(self, meta):
        self.meta.update(meta)
        db.getdb().instance.update({
            '_id': self.key,
        }, self.meta, upsert=True)

    def __repr__(self):
        return '{}({})'.format(self._classname, self.meta)

    def __eq__(self, o):
        return self.key == o.key

    def __lt__(self, o):
        return self.cmp_key < o.cmp_key

    def init(self):
        pass

    def store(self, *args, **kwargs):
        pass

    @property
    def cmp_key(self):
        return 0

    @property
    def _classname(self):
        return self.__class__.__name__
