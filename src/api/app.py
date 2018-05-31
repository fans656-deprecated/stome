import os
import time
import json
import functools
import traceback

import jwt
import flask

import conf
import util
import store
import fsutil
import filesystem
from errors import *
from user import User


app = Flask(__name__, template_folder='.')


def guarded(viewfunc):
    """
    Guard viewfunc to simplify result returning and exception handling

    Viewfunc can

        Return a Flask Response

        Return a dict like {'templates': []}

        Return a tuple like ({'detail': 'not found'}, 404)

        Raise a error.Error exception like Error('not found', 404)
    """
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        try:
            result = viewfunc(*args, **kwargs)

            if isinstance(result, flask.Response):
                return result

            if isinstance(result, tuple):
                errno = result[1]
                result = result[0]
            else:
                errno = 0

            if isinstance(result, dict):
                errno = 0
            ret = json.dumps()
        except Exception as e:
            exc = traceback.format_exc()
            print exc
            return exc, e.errno if hasattr(e, 'errno') else 400
    return decorated_viewfunc


@app.route('/', methods=['HEAD'])
@app.route('/<path:path>', methods=['HEAD'])
@guarded
def head_path(path=''):
    """Return 200 if path exists else 404"""
    if filesystem.exists(path):
        return '', 200
    else:
        return '', 404


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

        GET /img?meta
        GET /img/girl.jpg?meta

    # Query content transfer progress

        GET /video/SIRO-1690.wmv?transfer

    + Get storage templates

        GET /?storage-templates

    + Get storage instances

        GET /?storages

    + Get storage instance by name

        GET /?storage=vps
        GET /?storage=qiniu&op=get-upload-token

    + Query API page

        GET /?api
    """
    if 'api' in request.args:
        return render_template('api.html')

    visitor = get_visitor()

    if 'storage-templates' in request.args:
        return {'templates': store.storage.get_templates()}
    elif 'storage' in request.args:
        return handle_get_storage(request)
    elif 'storages' in request.args:
        return {'storages': store.storage.get_storages()}

    node = get_existed_node(path)

    if 'meta' in request.args:
        return node.get_meta(visitor)
    elif 'transfer' in request.args:
        return query_transfer_info(visitor, node)
    elif node.is_dir:
        return node.list(visitor, int(request.args.get('depth', 1)))
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

    + Create/Update file/directory metadata

        PUT /img?meta
        {
            "type": "dir"
        }

        PUT /img/girl.jpg?meta
        {
            "type": "file",
            "md5": "2b61c6d1ac994fc5ae83187928131552",
            "size": 13267,
            "mimetype": "image/jpeg"
        }

    # + Upload file

    #     PUT /img/girl.jpg
    #     <file-content>

    #     Parameters:

    #         md5: (required) full md5
    #         size: (required) total file size
    #         chunk-md5: (optional) chunk md5
    #         chunk-offset: (optional) chunk byte offset in file
    """
    visitor = get_visitor()
    if 'storage' in request.args:
        return handle_upsert_storage(visitor)
    elif 'meta' in request.args:
        return handle_upsert_node_meta(visitor, path)
    #else:
    #    return handle_upsert_node(visitor, path)


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


@app.route('/', methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
@guarded
def options_path(path=''):
    return ''


@app.after_request
def after_request(r):
    r.headers['Cache-Control'] = 'no-cache'
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = '*'
    r.headers['Access-Control-Allow-Headers'] = '*'
    return r


def handle_get_storage(request):
    storage_name = request.args.get('storage')
    if storage_name is None:
        return 'storage name not specified'

    storage = store.storage.get_by_name(storage_name)
    if not storage:
        return 'no storage named {}'.format(storage_name)

    op = request.args.get('op')
    if op:
        return storage.query(request)
    else:
        return storage


def handle_upsert_storage(visitor):
    meta = request.json
    storage = store.storage.get(meta.get('id'))
    storage.update(meta)
    return storage.meta


def handle_upsert_node_meta(visitor, path):
    meta = request.json
    node_type = meta['type']
    if node_type == 'dir':
        node = get_dir_node(path)
    elif node_type == 'file':
        node = get_file_node(path)
    if node.exists:
        node.create(visitor)
    node.update_meta(visitor, meta)
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
    node.content.write(
        request.stream,
        offset=int(request.args.get('chunk-offset', 0)),
        md5=request.args.get('chunk-md5')
    )


def query_transfer_info(visitor, node):
    if not visitor.can_read(node):
        raise CantRead(node)
    meta = dict(node.content.meta)
    unreceived = meta.get('unreceived', [])
    unreceived = sum(e - b for b, e in unreceived)
    meta['received'] = meta['size'] - unreceived
    return meta


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
