import jwt

import conf
import requests


def get_default_storage():
    return LocalStroage()


class LocalStroage(object):

    def save(self, md5, data, pos=0, part_size=None):
        if part_size is None:
            self.save_as_a_whole(md5, data)
        else:
            self.save_as_parts(md5, data, pos, part_size)

    def chunked_load(self, md5):
        return requests.get(
            get_file_url(md5),
            headers=get_auth_headers(),
            stream=True
        ).iter_content(1024 * 1024)

    def save_as_a_whole(self, md5, data):
        requests.put(get_file_url(md5), files={'data': data}, headers=get_auth_headers())

    def save_as_parts(self, md5, data, pos, part_size):
        requests.put(
            get_file_url(md5),
            data={'pos': pos, 'part-size': part_size},
            files={'data': data},
            headers=get_auth_headers()
        )


def get_file_url(md5):
    return conf.local_storage_server_origin + '/' + md5


def get_auth_headers():
    token = jwt.encode({'pubkey': conf.pubkey}, conf.prikey, 'RS512')
    headers = {'Authorization': 'Bearer ' + token}
    return headers
