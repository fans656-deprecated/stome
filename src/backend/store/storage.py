import db
import util
import store


def get_templates():
    return [m.template for m in store.storages.modules if m]


def get_storages():
    r = db.getdb().storage.find({}, {'_id': False})
    return list(r)


def get(id):
    meta = db.getdb().storage.find_one({'id': id}, {'_id': False})
    return Storage(meta)


class Storage(object):

    def __init__(self, meta):
        if meta:
            self.meta = meta
            self.exist = True
        else:
            self.meta = {'id': util.new_id()}
            self.exist = False

    @property
    def type(self):
        return self.meta['type']

    def update(self, meta):
        self.meta.update(meta)
        db.getdb().storage.update(
            {'id': self.meta['id']},
            self.meta,
            upsert=True
        )

    def delete(self):
        db.getdb().storage.remove({'id': self.meta['id']})

    def __repr__(self):
        return repr(self.meta)
