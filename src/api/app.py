import os
import time
import json
import functools
import traceback

import jwt
from flask import request, Response, Flask

import conf
import util
import store
import filesystem
from user import User
from error import Error, NotFound, Conflict


app = Flask(__name__, template_folder='.')


def guarded(viewfunc):
    """
    Guard viewfunc to simplify result returning and exception handling

    Viewfunc can

        Return a Flask Response, which will be used directly

        Return a dict like {'templates': []}, which will be JSONified

        Return a dict and a status code as tuple like
        ({'reason': 'not found'}, 404), former will be JSONfied,
        later will be used as status code

        Return None, then {'errno': 0} will be returned

        Raise a error.Error exception like Error('not found', 404), which
        will be turned into response like {'detail': 'not found'}, 404
    """
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        try:
            result = viewfunc(*args, **kwargs)

            if isinstance(result, Response):
                return result

            if isinstance(result, tuple):
                status_code = result[1]
                result = result[0]
            else:
                if result is None:
                    result = {'errno': 0}
                status_code = 200

            if isinstance(result, dict):
                ret = json.dumps(result, indent=2)
            elif isinstance(result, (str, unicode)):
                ret = result
            else:
                ret = ''

            return ret, status_code

        except Error as err:
            return json.dumps(err.result), err.errno
        except Exception as e:
            traceback.print_exc()
            return traceback.format_exc(), 500
    return decorated_viewfunc


@app.route('/', methods=['HEAD'])
@app.route('/<path:path>', methods=['HEAD'])
@guarded
def head_path(path=''):
    """Return 200 if path exists else 404"""
    visitor = get_visitor()
    node = filesystem.get_node(visitor, path)
    return '', 200 if node.exists else 404


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

    # TODO: access control
    if 'storage-templates' in request.args:
        return {'templates': store.storage.get_templates()}
    elif 'storage' in request.args:
        return handle_get_storage(request)
    elif 'storages' in request.args:
        return {'storages': store.storage.get_storages()}

    node = filesystem.get_node(visitor, path)
    if not node:
        raise NotFound(path)

    if 'meta' in request.args:
        return node.meta
    elif node.listable:
        depth = int(request.args.get('depth', 1))
        return node.list(depth)
    elif node.is_file:
        return node.get_content_stream()


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

    + Update file/directory metadata

        PUT /img/girl.jpg?meta
        {
            "type": "file",
            "md5": "2b61c6d1ac994fc5ae83187928131552",
            "size": 13267,
            "mimetype": "image/jpeg"
        }

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
    #else:
    #    return handle_upsert_node(visitor, path)


@app.route('/<path:path>', methods=['POST'])
@guarded
def post_path(path):
    """
    + Create directory

        POST /img?op=mkdir

    + Create file

        POST /img/girl.jpg?op=touch&md5=2b61c6d1ac994fc5ae83187928131552&size=32768

    + Rename file/directory

        POST /img/girl.jpg?op=mv
        {
            "to": "t.jpeg"
        }

    + Move file/directory

        POST /img/girl.jpg?op=mv
        {
            "to": "/public/girl.jpg"
        }

    + Copy file/directory

        POST /img/girl.jpg?op=cp
        {
            "to": "/public/girl.jpg"
        }
    """
    visitor = get_visitor()
    node = filesystem.get_node(visitor, path)
    op = request.args.get('op')
    if op == 'touch':
        size = int(request.args['size'])
        md5 = request.args['md5']
        mimetype = request.args['mimetype']
        node.create_as_file(size, md5, mimetype)
    elif op == 'mkdir':
        node.create_as_dir()
    #dst = get_dst_node(src, request.args.get('to'))
    #if op == 'mv':
    #    src.move(user, dst)
    #elif op == 'cp':
    #    dst.clone(user, src)


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
    visitor = get_visitor()
    if 'storage' in request.args:
        storage = store.storage.get(path)
        if not storage.exist:
            raise NotFound(path)
        storage.delete()
    else:
        filesystem.get_node(visitor, path).delete()


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


def handle_update_node_meta(visitor, path):
    node = filesystem.get_node(visitor, path)
    meta = request.json
    node.update_meta(meta)
    # TODO: update meta


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
    user = {'username': 'root'}
    #try:
    #    token = request.headers['authorization'].split(' ')[1]
    #    user = jwt.decode(token, conf.auth_pubkey, algorithm='RS512')
    #    if not fsutil.get_home_dir(user).exist:
    #        fsutil.create_home_dir_for(user)
    #except Exception as e:
    #    user = {'username': 'guest'}
    return User(user)


def get_dst_node(src, to):
    if not to.startswith('/'):
        to = src.parent.path + '/' + to
    return filesystem.get_node(to)


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
        from tests.prepare import init
        init()
    if not filesystem.initialized():
        filesystem.initialize()
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=debug)
