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

    + Get storages

        GET /?storages

    + Query API page

        GET /?api
    """
    if 'api' in request.args:
        return render_template('api.html')

    visitor = get_visitor()

    # TODO: access control
    if 'storage-templates' in request.args:
        return {'templates': store.storage.get_templates()}
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

    + Update file/directory meta

        PUT /img/girl.jpg?meta
        {
            "type": "file",
            "md5": "2b61c6d1ac994fc5ae83187928131552",
            "size": 13267,
            "mimetype": "image/jpeg"
        }

    + Update content meta

        PUT /?content
        {
            "md5": "2b61c6d1ac994fc5ae83187928131552",
            "storage_id": "ac994f792813c5ae822b63181551c6d1",
            "status": "done"
        }
    """
    visitor = get_visitor()
    if 'storage' in request.args:
        return handle_upsert_storage(visitor)
    elif 'meta' in request.args:
        return handle_update_node_meta(visitor, path)
    elif 'content' in request.args:
        return handle_update_content_meta(visitor)
    #else:
    #    return handle_upsert_node(visitor, path)


@app.route('/', methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
@guarded
def post_path(path=''):
    """
    + Create directory

        POST /img?op=mkdir

    + Create file

        POST /img/girl.jpg
            ?op=touch
            &md5=2b61c6d1ac994fc5ae83187928131552
            &size=32768

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

    + Content query

        POST /?op=content-query
        {
            "op": "prepare-upload",
            "md5": "76dd0f1ea2f000b5f1a19c0b5198da84",
            "storage_id": "07a6211ede979e3b0c391f54d699f2ac"
        }
    """
    visitor = get_visitor()
    op = request.args.get('op')

    if op == 'content-query':
        return handle_content_query()

    node = filesystem.get_node(visitor, path)
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
    print 'deleting', path
    visitor = get_visitor()
    if 'storage' in request.args:
        storage = store.storage.get(path)
        if not storage.exist:
            raise NotFound(path)
        storage.delete()
    else:
        node = filesystem.get_node(visitor, path)
        print 'got node', node
        node.delete()


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


def handle_content_query():
    q = request.json
    md5 = q['md5']
    storage_id = q['storage_id']
    content = store.content.get(md5, storage_id)
    if not content:
        raise NotFound(content.id)
    return content.query(q)


def handle_upsert_storage(visitor):
    meta = request.json
    storage = store.storage.get(meta.get('id'))
    storage.update(meta)
    return storage.meta


def handle_update_node_meta(visitor, path):
    # TODO: access control
    node = filesystem.get_node(visitor, path)
    meta = request.json
    node.update_meta(meta)

def handle_update_content_meta(visitor):
    # TODO: access control
    meta = request.json
    content = store.content.get(meta['md5'], meta['storage_id'])
    content.update_meta(meta)


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
    print 'Initializing...'
    if not filesystem.initialized():
        filesystem.initialize()
    print 'Initialized'
    app.run(
        host='0.0.0.0',
        port=conf.port,
        threaded=True,
        debug=True,
        ssl_context='adhoc',
    )
