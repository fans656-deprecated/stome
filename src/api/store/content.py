import os
import hashlib

import conf
from db import getdb


class Content(object):

    def __init__(self, id, md5=None):
        meta = getdb().content.find_one({'id': id}, {'_id': False})
        if meta:
            self.meta = meta
            if meta['md5'] != md5:
                self._update_meta({'md5': md5})
            self.exist = True
        else:
            self.meta = {
                'id': id,
                'md5': md5,
            }
            self.exist = False

    @property
    def id(self):
        return self.meta['id']

    @property
    def md5(self):
        return self.meta['md5']

    @property
    def status(self):
        return self.meta['status']

    @property
    def size(self):
        return self.meta['size']

    @property
    def storages(self):
        return self.meta['storages']

    @property
    def unreceived(self):
        return Ranges(*self.meta.get('unreceived'))

    @unreceived.setter
    def unreceived(self, new_unreceived):
        self._update_meta({'unreceived': list(new_unreceived)})

    def create(self, size):
        if not size:
            raise RuntimeError()
        self.meta.update({
            'status': 'init',
            'size': size,
            'unreceived': [(0, size)],
            'storages': self.meta.get('storages', []),
        })
        self._invalidate_storages()
        self._create_transfer_file()
        self._update_meta(self.meta, upsert=True)
        return self

    def write(self, data, offset=0, md5=None):
        self._start_transfer()
        if hasattr(data, 'read'):
            r = self._write_stream(data, offset, md5)
        else:
            r = self._write_data(data, offset, md5)
        if not self.unreceived:
            self._start_verify()
        return r

    def _write_data(self, data, offset=0, md5=None):
        chunk_range = (offset, offset + len(data))
        if md5 and util.calc_md5(data) != md5:
            return chunk_range
        with self._open_transfer_file() as f:
            f.seek(offset, os.SEEK_SET)
            f.write(data)
            self.unreceived -= (chunk_range)
        return None

    def _write_stream(self, stream, offset=0, md5=None):
        with self._open_transfer_file() as f:
            m = hashlib.md5()
            chunk_offset = offset
            while True:
                data = stream.read(conf.CHUNK_SIZE)
                if not data:
                    break
                f.seek(offset, os.SEEK_SET)
                f.write(data)
                offset += len(data)
                if md5:
                    m.update(data)
            chunk_range = chunk_offset, offset
            if md5 and m.hexdigest() != md5:
                self.unreceived += chunk_range
                return chunk_range
            else:
                self.unreceived -= chunk_range
                return None

    def _start_transfer(self):
        self._transit_to('transferring')

    def _start_verify(self):
        self._transit_to('verifying')
        md5 = self._calc_full_md5()
        if self.md5 and self.md5 != md5:
            self._fail_verify()
        else:
            self._update_meta({'md5': md5})
            self._start_store()

    def _fail_verify(self):
        self.create(self.size)

    def _start_store(self):
        self._transit_to('storing')

    def _transit_to(self, status):
        self._update_meta({'status': status})

    def _invalidate_storages(self):
        storages = self.storages
        for storage in storages:
            storage['status'] = 'init'

    def _open_transfer_file(self):
        return open(self._get_transfer_fpath(), 'rb+')

    def _create_transfer_file(self):
        fpath = self._get_transfer_fpath()
        if not os.path.exists(fpath):
            if not os.path.exists(conf.transfer_root):
                os.makedirs(conf.transfer_root)
            open(fpath, 'wb').close()

    def _get_transfer_fpath(self):
        return os.path.join(conf.transfer_root, self.id)

    def _update_meta(self, meta, upsert=False, delete=False):
        self.meta.update(meta)
        if upsert:
            getdb().content.update({'id': self.id}, meta, upsert=True)
        else:
            getdb().content.update({'id': self.id}, {'$set': meta})

    def _calc_full_md5(self):
        m = hashlib.md5()
        with self._open_transfer_file() as f:
            chunk = f.read(conf.CHUNK_SIZE)
            m.update(chunk)
        return m.hexdigest()

    def __repr__(self):
        return repr(self.meta)


class Ranges(object):

    def __init__(self, *ranges):
        self.a = list(ranges)

    def insert(self, (beg, end)):
        if not self.a:
            self.a.append((beg, end))
            return
        a = self.a
        a.append((beg, end))
        a.sort(key=lambda r: r[0])
        b = [a[0]]
        for beg, end in a[1:]:
            _beg, _end = b[-1]
            if beg != _end:
                new_beg = min(beg, _beg)
                new_end = max(end, _end)
                b[-1] = (new_beg, new_end)
            else:
                b.append((beg, end))
        self.a = b

    def delete(self, (beg, end)):
        b = []
        for _beg, _end in self.a:
            if _end < beg or _beg > end:
                b.append((_beg, _end))
                continue
            ibeg = max(beg, _beg)
            iend = min(end, _end)
            if _beg < ibeg:
                b.append((_beg, ibeg))
            if iend < _end:
                b.append((iend, _end))
        self.a = b

    def __nonzero__(self):
        return bool(self.a)

    def __iadd__(self, rg):
        self.insert(rg)
        return self

    def __isub__(self, rg):
        self.delete(rg)
        return self

    def __iter__(self):
        return iter(self.a)

    def __repr__(self):
        return repr(self.a)


if False:
    """
Content status transition:

        create => {init}
    {init}
        first write begin => {transferring}
    {transferring}
        last write done => {verifying}
    {verifying}
        verify failed => {init}
        verified => {storing}
    {storing}
        first storage done => {done}
    {done}

    """
