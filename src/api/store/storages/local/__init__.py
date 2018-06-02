import os

import db
import conf
import store


template = {
    'type': 'local',
    'name': 'vultr',
    'root': '~/.stome-files',
}


class StorageInstanceLocal(store.instance.Instance):

    def init(self):
        self.update_meta({
        })

    def store(self, transfer_fpath, on_done=None):
        db.use_new()
        src_path = transfer_fpath
        dst_path = self.fpath
        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        os.system('cp -r {} {}'.format(src_path, dst_path))
        assert os.path.exists(dst_path)
        self.update_meta({
            'status': 'done'
        })
        if on_done:
            on_done(self)

    @property
    def fpath(self):
        return os.path.join(self.get_root_path(), self.md5)

    def get_root_path(self):
        path = self.storage.meta['root']
        if '~' in path:
            path = os.path.expanduser(path)
        path = os.path.abspath(path)
        return path

    def iter(self):
        with open(self.fpath, 'rb') as f:
            while True:
                data = f.read(conf.CHUNK_SIZE)
                if not data:
                    break
                yield data

    @property
    def cmp_key(self):
        return 100

Instance = StorageInstanceLocal
