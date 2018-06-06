import os

import db
import conf
import store


template = {
    'type': 'local',
    'name': 'vultr',
    'root': '~/.stome-files',
}


class LocalContent(store.content.Content):

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


Content = LocalContent


#
#    def add_unreceived(self, chunk_range):
#        self.change_unreceived(chunk_range, add=True)
#
#    def remove_unreceived(self, chunk_range):
#        self.change_unreceived(chunk_range, add=False)
#
#    def change_unreceived(self, chunk_range, add=True):
#        while True:
#            unreceived, version = self._get_unreceived_with_version()
#            if add:
#                unreceived += chunk_range
#            else:
#                unreceived -= chunk_range
#            res = db.getdb().content.find_one_and_update(
#                {'md5': self.md5, 'unreceived_version': version},
#                {
#                    '$set': {
#                        'unreceived': list(unreceived),
#                        'unreceived_version': version + 1,
#                    }
#                }
#            )
#            if res:
#                break
#        self.meta.update({'unreceived': list(unreceived)})
#
#    def _get_unreceived_with_version(self):
#        meta = db.getdb().content.find_one(
#            self._db_find_key,
#            {
#                'unreceived': 1,
#                'unreceived_version': 1,
#                '_id': 0,
#            }
#        )
#        return Ranges(*meta['unreceived']), meta['unreceived_version']
#
#    @property
#    def _db_find_key(self):
#        return {'md5': self.md5}
#
#    def iter(self):
#        instances = sorted(ins for ins in self.instances if ins.done)
#        return instances[0].iter_content()
#
#    def create(self, size):
#        self.meta.update({
#            'status': 'init',
#            'size': size,
#            'unreceived': [(0, size)],
#            'unreceived_version': 0,
#            'storage_ids': [],
#        })
#        self._create_transfer_file()
#        self._update_meta(self.meta, upsert=True)
#        return self
#
#    def write(self, data, offset=0, md5=None):
#        self._start_transfer()
#        self._write_stream(data, offset, md5)
#        if not self.unreceived:
#            self._start_verify()
#
#    def _write_stream(self, stream, offset=0, md5=None):
#        with self._open_transfer_file() as f:
#            m = hashlib.md5()
#            chunk_offset = offset
#            while True:
#                data = stream.read(conf.CHUNK_SIZE)
#                if not data:
#                    break
#                f.seek(offset, os.SEEK_SET)
#                f.write(data)
#                offset += len(data)
#                if md5:
#                    m.update(data)
#            chunk_range = chunk_offset, offset
#            if md5 and m.hexdigest() != md5:
#                self.add_unreceived(chunk_range)
#            else:
#                self.remove_unreceived(chunk_range)
#
#    def _start_transfer(self):
#        if self.status != 'transferring':
#            self._update_meta({
#                'unreceived': [(0, self.size)],
#                'unreceived_version': 0
#            })
#            self._create_transfer_file()
#            self._transit_to('transferring')
#
#    def _start_verify(self):
#        self._update_meta({'unreceived_version': 0})
#        self._transit_to('verifying')
#        return
#        md5 = self._calc_full_md5()
#        if self.md5 and self.md5 != md5:
#            self._fail_verify()
#        else:
#            self._start_store()
#
#    def _fail_verify(self):
#        self.create(self.size)
#
#    def _start_store(self):
#        self._transit_to('storing')
#        pool = store.pool.get()
#        for instance in self.instances:
#            pool.run(
#                instance.key,
#                instance.store,
#                self._transfer_fpath,
#                on_done=self._on_store_done,
#            )
#
#    def _on_store_done(self, instance):
#        if self.status == 'storing':
#            print 'done'
#            self._transit_to('done')
#
#    @property
#    def _transfer_fpath(self):
#        return os.path.join(conf.transfer_root, self.md5)
#
#    def _transit_to(self, status):
#        self._update_meta({'status': status})
#
#    def _open_transfer_file(self):
#        return open(self._transfer_fpath, 'rb+')
#
#    def _create_transfer_file(self):
#        fpath = self._transfer_fpath
#        if not os.path.exists(fpath):
#            if not os.path.exists(conf.transfer_root):
#                os.makedirs(conf.transfer_root)
#            open(fpath, 'wb').close()
#
#    def _update_meta(self, meta, upsert=False, delete=False):
#        self.meta.update(meta)
#        if upsert:
#            db.getdb().content.update({'md5': self.md5}, meta, upsert=True)
#        else:
#            db.getdb().content.update({'md5': self.md5}, {'$set': meta})
#
#    def _calc_full_md5(self):
#        m = hashlib.md5()
#        with self._open_transfer_file() as f:
#            while True:
#                chunk = f.read(conf.CHUNK_SIZE)
#                if not chunk:
#                    break
#                m.update(chunk)
#        return m.hexdigest()
#
#    def _add_instance(self, instance):
#        instance.ref_count += 1
#        self._update_meta({
#            'storage_ids': self.storage_ids + [instance.storage_id]
#        })
#
#    def __repr__(self):
#        return json.dumps(self.meta, indent=2)
#
#
#class Ranges(object):
#
#    def __init__(self, *ranges):
#        self.a = list(ranges)
#
#    def insert(self, (beg, end)):
#        if not self.a:
#            self.a.append((beg, end))
#            return
#        a = self.a
#        a.append((beg, end))
#        a.sort(key=lambda r: r[0])
#        b = [a[0]]
#        for beg, end in a[1:]:
#            _beg, _end = b[-1]
#            if beg != _end:
#                new_beg = min(beg, _beg)
#                new_end = max(end, _end)
#                b[-1] = (new_beg, new_end)
#            else:
#                b.append((beg, end))
#        self.a = b
#
#    def delete(self, (beg, end)):
#        b = []
#        for _beg, _end in self.a:
#            if _end < beg or _beg > end:
#                b.append((_beg, _end))
#                continue
#            ibeg = max(beg, _beg)
#            iend = min(end, _end)
#            if _beg < ibeg:
#                b.append((_beg, ibeg))
#            if iend < _end:
#                b.append((iend, _end))
#        self.a = b
#
#    def __nonzero__(self):
#        return bool(self.a)
#
#    def __iadd__(self, rg):
#        self.insert(rg)
#        return self
#
#    def __isub__(self, rg):
#        self.delete(rg)
#        return self
#
#    def __iter__(self):
#        return iter(self.a)
#
#    def __repr__(self):
#        return repr(self.a)
