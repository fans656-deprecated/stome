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
from user import User
from node import get_node, get_existed_node, get_file_node, get_dir_node


app = Flask(__name__, template_folder='.')


def handle_exceptions(viewfunc):
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        try:
            r = viewfunc(*args, **kwargs)
            return json.dumps(r) if r else 'ok'
        except Exception as e:
            traceback.print_exc()
            return str(e), e.errno
    return decorated_viewfunc


@app.route('/')
@app.route('/<path:path>')
@handle_exceptions
def get_path(path=''):
    """
    + Download file

        GET /img/girl.jpg

    + List directory

        GET /img

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
        return json.dumps(store.storage.get_templates())
    elif node.is_dir:
        return node.list(visitor)
    elif node.is_file:
        return make_content_stream(node)


@app.route('/<path:path>', methods=['PUT'])
@handle_exceptions
def put_path(path):
    """
    1. Upload file

        PUT /img/girl.jpg
        <file-content>

        Parameters:

            md5: full md5
            chunk-md5: chunk md5
            chunk-offset: chunk byte offset in file

    2. Create directory

        PUT /img/

    3. Modify file/directory metadata

        PUT /img/girl.jpg?meta
        {
            "access": 0600,
            "size": 13267,
        }
    """
    visitor = get_visitor()
    if path.endswith('/'):
        node = get_dir_node(path)
    else:
        node = get_file_node(path)
    if not node.exist:
        node.create(visitor)
    if 'meta' in request.args:
        return node.update_meta(visitor, request.json)
    else:
        return handle_upload(visitor, node)


@app.route('/<path:path>', methods=['POST'])
@handle_exceptions
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
def delete_path(path):
    """
    Delete file/directory

        DELETE /img
        DELETE /img/girl.jpg
    """
    get_existed_node(path).remove(get_visitor(), recursive=True)


@app.after_request
def after_request(r):
    r.headers['Cache-Control'] = 'no-cache'
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = '*'
    return r


def get_visitor():
    try:
        token = request.headers['authorization'].split(' ')[1]
        user = jwt.decode(token, conf.auth_pubkey, algorithm='RS512')
        if not fsutil.get_home_dir(user).exist:
            fsutil.create_home_dir_for(user)
    except Exception as e:
        user = {'username': 'guest'}
    return User(user)


def get_dst_node(src, to):
    if not to.startswith('/'):
        to = src.parent.path + '/' + to
    return get_node(to)


def make_content_stream(node):
    return Response(node.iter_data(), mimetype=node.mimetype)


def is_simple_upload():
    return 'pos' not in request.args


def handle_upload(visitor, node):
    md5 = request.args.get('md5')
    if md5:
        content = store.get_content(id=md5, md5=md5)
    else:
        md5 = util.calc_md5(visitor.username + node.path)
        content = store.get_content(id=md5)
    size = request.args.get('size')
    if not content.exist or size != content.size:
        if size is None and 'offset' not in request.args:
            size = request.headers['content-length']
        content.create(size or node.size)
    node.update_meta(visitor, {'md5': md5})

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
