class User(object):

    def __init__(self, meta):
        if 'groups' not in meta:
            meta['groups'] = [meta['username']]
        self.meta = meta

    def __getitem__(self, key):
        return self.meta.__getitem__(key)

    def __repr__(self):
        return repr(self.meta)


if __name__ == '__main__':
    u = User({'username': 'guest'})
    print u.meta
