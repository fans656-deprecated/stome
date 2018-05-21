import storages


def get_templates():
    return [mod.template for mod in storages.modules if mod]


class Storage(object):

    def __init__(self, meta):
        self.meta = meta
