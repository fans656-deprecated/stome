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
from node import (
    get_node,
    get_existed_node,
    get_file_node,
    get_dir_node,
    get_dir_or_file_node,
)


app = Flask(__name__, template_folder='.')


def guarded(viewfunc):
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        try:
            r = viewfunc(*args, **kwargs)
            if isinstance(r, Response):
                return r
            else:
                return json.dumps(r or {'errno': 0})
        except Exception as e:
            exc = traceback.format_exc()
            print exc
            return exc, e.errno if hasattr(e, 'errno') else 400
    return decorated_viewfunc


@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
@guarded
def options_path(path=''):
    return ''


@app.route('/', methods=['HEAD'])
@app.route('/<path:path>', methods=['HEAD'])
@guarded
def head_path(path=''):
    get_existed_node(path)


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
            storage = store.get_storage(name)
            if not storage:
                raise NotFound(name)
            return storage
    elif 'storages' in request.args:
        return {'storages': store.storage.get_storages()}
    elif node.is_dir:
        depth = int(request.args.get('depth', 1))
        return node.list(visitor, depth)
    elif node.is_file:
        return make_content_stream(visitor, node)


@app.route('/', methods=['PUT'])
@app.route('/<path:path>', methods=['PUT'])
@guarded
def put_path(path='/'):
    """
    + Create/Update storage

        PUT /?storage
        {
            "type": "local",
            "name": "vultr",
            "root": "~/.stome-files"
        }

    + Modify file/directory metadata

        PUT /img/girl.jpg?meta
        {
            "access": 0600,
            "size": 13267,
        }

    + Create directory

        PUT /img/

    + Upload file

        PUT /img/girl.jpg
        <file-content>

        Parameters:

            md5: (required) full md5
            size: (required) total file size
            chunk-md5: (optional) chunk md5
            chunk-offset: (optional) chunk byte offset in file
    """
    visitor = get_visitor()
    if 'storage' in request.args:
        return handle_upsert_storage(visitor)
    elif 'meta' in request.args:
        return handle_update_node_meta(visitor, path)
    else:
        return handle_upsert_node(visitor, path)


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
        storage = store.get_storage(path)
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


def handle_upsert_storage(visitor):
    meta = request.json
    storage = store.get_storage(meta.get('id'))
    storage.update(meta)
    return storage.meta


def handle_update_node_meta(visitor, path):
    node = get_existed_node(path)
    node.update_meta(visitor, request.json)
    return node.inherited_meta


def handle_upsert_node(visitor, path):
    node = get_dir_or_file_node(path)
    if node.is_dir:
        if not node.exists:
            node.create(visitor)
    elif node.is_file:
        size = get_content_size()
        md5 = request.args.get('md5')
        if not node.exists:
            mimetype = request.headers.get('content-type')
            node.create(visitor, size=size, md5=md5, mimetype=mimetype)
        handle_upload(node, size, md5)


def handle_upload(node, size, md5):
    content = node.content
    failed_bytes_range = content.write(
        request.stream,
        offset=int(request.args.get('chunk-offset', 0)),
        md5=request.args.get('chunk-md5')
    )
    if failed_bytes_range:
        return json.dumps({
            'failed': failed_bytes_range,
        })


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


def make_content_stream(visitor, node):
    return Response(node.iter_content(visitor), mimetype=node.mimetype)


def is_simple_upload():
    return 'pos' not in request.args


def get_content_size():
    size = request.args.get('size', 0) or request.headers['content-length']
    return int(size)


if __name__ == '__main__':
    debug = True
    if debug:
        import test.setup
    if not fsutil.initialized():
        fsutil.create_root_dir()
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=debug)
