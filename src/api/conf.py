import os
import store


auth_pubkey_fpath = os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')
auth_pubkey = open(auth_pubkey_fpath).read().strip()
port = 6001

_script_root = os.path.dirname(os.path.realpath(__file__))
_project_root = os.path.dirname(os.path.dirname(_script_root))

local_storage_root = os.path.join(_project_root, 'files/local')
transfer_root = os.path.join(_project_root, 'files/transfer')


CHUNK_SIZE = 4096


if __name__ == '__main__':
    print dir(store.storages.local)
    print store.storages.local.template
