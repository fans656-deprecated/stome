import os


auth_pubkey_fpath = os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')
auth_pubkey = open(auth_pubkey_fpath).read().strip()
port = 6001

frontend_path = '../frontend/build'

_script_root = os.path.dirname(os.path.realpath(__file__))
_project_root = os.path.dirname(os.path.dirname(_script_root))

local_storage_root = os.path.join(_project_root, 'files/local')
transfer_root = os.path.join(_project_root, 'files/transfer')


KB = 1024
MB = 1024 * KB
CHUNK_SIZE = 4 * MB
