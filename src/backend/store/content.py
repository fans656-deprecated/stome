import os
import json
import hashlib

import db
import conf
import store


def get(md5, storage_id):
    storage = store.storage.get(storage_id)
    storage_type = storage.type
    module = getattr(store.storages, storage_type)
    Content = getattr(module, 'Content')

    content_id = make_id(md5, storage_id)
    meta = db.getdb().content.find_one({'_id': content_id})
    if meta:
        content = Content(meta, True)
    else:
        meta = {
            'md5': md5,
            'storage_id': storage_id,
            'status': 'init',
            'ref_count': 1,
            '_id': content_id,
        }
        content = Content(meta, False)
    content.init_extra()
    return content


class Content(object):

    def __init__(self, meta, exists):
        self._meta = meta
        self.exists = exists

    @property
    def meta(self):
        storage = store.storage.get(self.storage_id)
        meta = dict(self._meta)
        del meta['_id']
        meta.update({
            'type': storage.type,
        })
        return meta

    @property
    def md5(self):
        return self._meta['md5']

    @property
    def storage_id(self):
        return self._meta['storage_id']

    @property
    def status(self):
        return self._meta['status']

    @property
    def ref_count(self):
        return self._meta['ref_count']

    @ref_count.setter
    def ref_count(self, count):
        if count:
            self.update_meta({'ref_count': count})
        else:
            self.delete()

    @property
    def id(self):
        return self._meta['_id']

    @property
    def storage(self):
        return store.storage.get(self.storage_id)

    def create(self):
        db.getdb().content.insert_one(self._meta)

    def delete(self):
        self.delete_content()
        db.getdb().content.remove({'_id': self.id})

    def update_meta(self, meta):
        self._meta.update(meta)
        self.serialize()

    def serialize(self):
        db.getdb().content.update({'_id': self.id}, self._meta)

    def __nonzero__(self):
        return self.exists

    def init_extra(self):
        pass

    def query(self, args):
        pass

    def delete_content(self):
        pass


def make_id(md5, storage_id):
    return md5 + '-' + storage_id
