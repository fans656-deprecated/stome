from db import getdb
from content import Content


__all__ = [
    'get_storages',
    'add_storage',
    'get_content',
]


def get_storages():
    return list(getdb().storage.find({}))


def add_storage(meta):
    st = Storage(meta)
    print st


def get_content(id, md5=None):
    return Content(id, md5=md5)
