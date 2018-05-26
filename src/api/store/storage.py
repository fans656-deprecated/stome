import util
import storages
from db import getdb


def get_templates():
    return [mod.template for mod in storages.modules if mod]


def get_storages():
    r = getdb().storage.find({}, {'_id': False})
    return list(r)


def get_storage(id):
    meta = getdb().storage.find_one({'id': id}, {'_id': False})
    return Storage(meta)


class Storage(object):

    def __init__(self, meta):
        if meta:
            self.meta = meta
            self.exist = True
        else:
            self.meta = {'id': util.new_id()}
            self.exist = False

    def update(self, meta):
        self.meta.update(meta)
        getdb().storage.update({'id': self.meta['id']}, self.meta, upsert=True)

    def delete(self):
        getdb().storage.remove({'id': self.meta['id']})
