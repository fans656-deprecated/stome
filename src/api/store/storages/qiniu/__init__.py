import os
import json

import qiniu

from conf import CHUNK_SIZE
import store


keys_fpath = os.path.expanduser('~/.qiniu/keys.json')
if os.path.exists(keys_fpath):
    with open(keys_fpath) as f:
        keys = json.load(f)
    access_key = keys['access-key']
    secret_key = keys['secret-key']
else:
    access_key = '<your-access-key>'
    secret_key = '<your-secret-key>'


template = {
    'type': 'qiniu',
    'name': 'qiniu',
    'domain': 'https://p9jlgsz5w.bkt.clouddn.com/',
    'bucket': 'eno-zone',
    'access-key': access_key,
    'secret-key': secret_key,
}


class QiniuContent(store.content.Content):

    def init_extra(self):
        storage = self.storage
        access_key = storage.meta['access-key']
        secret_key = storage.meta['secret-key']
        self.domain = storage.meta['domain']
        self.auth = qiniu.Auth(access_key, secret_key)
        self.bucket_manager = qiniu.BucketManager(self.auth)
        self.bucket_name = storage.meta['bucket']

    def query(self, args):
        op = args['op']
        if op == 'prepare-upload':
            return self.prepare_upload(args)
        elif op == 'get-upload-token':
            return self.get_upload_token(args)
        elif op == 'get-download-url':
            return self.get_download_url(args)

    def delete_content(self):
        chunks = self.meta['chunks']
        ops = qiniu.build_batch_delete(
            self.bucket_name, [c['path'] for c in chunks]
        )
        print 'QiniuContent.delete_content'
        self.bucket_manager.batch(ops)
        print 'QiniuContent.delete_content done'

    def prepare_upload(self, args):
        size = args['size']
        chunks = []
        n_chunks = (size + CHUNK_SIZE - 1) // CHUNK_SIZE
        for i_chunk in xrange(n_chunks):
            offset = i_chunk * CHUNK_SIZE
            chunk_size = min(CHUNK_SIZE, size - offset)
            chunk = self.make_chunk(i_chunk, n_chunks, offset, chunk_size)
            chunks.append(chunk)
        self.update_meta({'chunks': chunks})
        return {'chunks': chunks}

    def get_upload_token(self, args):
        path = args['path']
        token = self.make_upload_token(path)
        return {'token': token}

    def get_download_url(self, args):
        path = args['path']
        baseurl = self.domain + ('' if self.domain.endswith('/') else '/') + path
        url = self.auth.private_download_url(baseurl, expires=3600)
        return {'url': url}

    def make_chunk(self, i_chunk, n_chunks, offset, size):
        if n_chunks == 1:
            path = self.md5
        else:
            path = self.md5 + '-{}-{}'.format(i_chunk, n_chunks)
        return {
            'path': path,
            'offset': offset,
            'size': size,
        }

    def make_upload_token(self, path):
        bucket = self.bucket_name
        token = self.auth.upload_token(bucket, path, 3600)
        return token


Content = QiniuContent
