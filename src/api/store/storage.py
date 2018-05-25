import storages


def get_templates():
    return [mod.template for mod in storages.modules if mod]


def get_storages():
    return []


def get_storage(name):
    return None


class Storage(object):

    def __init__(self, meta):
        self.meta = meta
