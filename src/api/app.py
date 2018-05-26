import os
import json
import functools
import traceback

import jwt
from flask import *

import conf
import util
import store
import fsutil
from errors import *
from user import User
from node import get_node, get_existed_node, get_file_node, get_dir_node


app = Flask(__name__, template_folder='.')


def guarded(viewfunc):
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        try:
            r = viewfunc(*args, **kwargs)
            return json.dumps(r or {'errno': 0})
        except Exception as e:
            exc = traceback.format_exc()
            print exc
            return exc, e.errno if hasattr(e, 'errno') else 400
    return decorated_viewfunc


@app.route('/')
@app.route('/<path:path>')
@guarded
def get_path(path=''):
    """
    + Download file

        GET /img/girl.jpg

    + List directory

        GET /img?depth=2

    + Retrieve file/directory metadata

        GET /img?meta=true
        GET /img/girl.jpg?meta=true
        {
            "custom": {
                "transfer": {
                    "progress": {}
                }
            }
        }

    + Get storage templates

        GET /?storage-templates

    + Get storage instances

        GET /?storages

    + Get storage instance by name

        GET /?storage=vps

    + Query API page

        GET /?api=true
    """
    if 'api' in request.args:
        return render_template('api.html')

    visitor = get_visitor()
    node = get_existed_node(path)

    if 'meta' in request.args:
        return node.get_meta(visitor)
    elif 'storage-templates' in request.args:
        return {'templates': store.storage.get_templates()}
    elif 'storage' in request.args:
        name = request.args.get('storage')
        if name:
            storage = store.storage.get_storage(name)
            if not storage:
                raise NotFound(name)
            return storage
    elif 'storages' in request.args:
        return {'storages': store.storage.get_storages()}
    elif node.is_dir:
        depth = int(request.args.get('depth', 1))
        return node.list(visitor, depth)
    elif node.is_file:
        return make_content_stream(node)


@app.route('/', methods=['PUT'])
@app.route('/<path:path>', methods=['PUT'])
@guarded
def put_path(path='/'):
    """
    + Upload file

        PUT /img/girl.jpg
        <file-content>

        Parameters:

            md5: (required) full md5
            size: (required) total file size
            chunk-md5: (optional) chunk md5
            chunk-offset: (optional) chunk byte offset in file

    + Create directory

        PUT /img/

    + Modify file/directory metadata

        PUT /img/girl.jpg?meta
        {
            "access": 0600,
            "size": 13267,
        }
    """
    visitor = get_visitor()
    if 'storage' in request.args:
        meta = request.json
        storage = store.storage.get_storage(meta.get('id'))
        storage.update(meta)
        return storage.meta
    if path.endswith('/'):
        node = get_dir_node(path)
        size = 0
        md5 = None
    else:
        node = get_file_node(path)
        size = get_content_size()
        md5 = request.args['md5']
    if not node:
        node.create(visitor, size=size, md5=md5)
    #if 'meta' in request.args:
    #    return node.update_meta(visitor, request.json)._get_meta()
    #else:
    #    return handle_upload(node, size, md5)


@app.route('/<path:path>', methods=['POST'])
@guarded
def post_path(path):
    """
    1. Rename file/directory

        POST /img/girl.jpg?op=mv
        {
            "to": "t.jpeg"
        }

    2. Move file/directory

        POST /img/girl.jpg?op=mv
        {
            "to": "/public/girl.jpg"
        }

    3. Copy file/directory

        POST /img/girl.jpg?op=cp
        {
            "to": "/public/girl.jpg"
        }
    """
    visitor = get_visitor()
    op = request.args.get('op')
    src = get_existed_node(path)
    dst = get_dst_node(src, request.args.get('to'))
    if op == 'mv':
        src.move(user, dst)
    elif op == 'cp':
        dst.clone(user, src)


@app.route('/<path:path>', methods=['DELETE'])
@guarded
def delete_path(path):
    """
    Delete file/directory

        DELETE /img
        DELETE /img/girl.jpg

    Delete storage

        DELETE /20180402_231528_2039_UTC?storage
    """
    if 'storage' in request.args:
        storage = store.storage.get_storage(path)
        if not storage.exist:
            raise NotFound(path)
        storage.delete()
    else:
        get_existed_node(path).remove(get_visitor(), recursive=True)


@app.after_request
def after_request(r):
    r.headers['Cache-Control'] = 'no-cache'
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = '*'
    r.headers['Access-Control-Allow-Headers'] = '*'
    return r


def get_visitor():
    try:
        token = request.headers['authorization'].split(' ')[1]
        user = jwt.decode(token, conf.auth_pubkey, algorithm='RS512')
        if not fsutil.get_home_dir(user).exist:
            fsutil.create_home_dir_for(user)
    except Exception as e:
        user = {'username': 'guest'}
        # DEBUG
        user = {'username': 'root'}
    return User(user)


def get_dst_node(src, to):
    if not to.startswith('/'):
        to = src.parent.path + '/' + to
    return get_node(to)


def make_content_stream(node):
    return Response(node.iter_data(), mimetype=node.mimetype)


def is_simple_upload():
    return 'pos' not in request.args


def get_content_size():
    size = request.args.get('size', 0) or request.headers['content-length']
    return int(size)


def handle_upload(node, size, md5):
    content = node.content
    failed_bytes_range = content.write(
        request.stream,
        offset=request.args.get('offset', 0),
        md5=request.args.get('chunk-md5')
    )
    if content.status == 'done':
        node.update_meta({
            'md5': content.md5,
            'size': content.size,
        })
        content.ref += 1
    if failed_bytes_range:
        return json.dumps({
            'failed': failed_bytes_range,
        })


if __name__ == '__main__':
    debug = True
    if debug:
        import test.setup
    if not fsutil.initialized():
        fsutil.create_root_dir()
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=debug)
