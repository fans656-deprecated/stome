import os
import json
import functools
import traceback

from flask import *

import conf
import fsutil
from user import User
from node import get_node, get_existed_node


app = Flask(__name__, template_folder='.')


def handle_exceptions(viewfunc):
    @functools.wraps(viewfunc)
    def decorated_viewfunc(*args, **kwargs):
        r = viewfunc(*args, **kwargs)
        return json.dumps({
            'errno': 200,
            'res': r or '',
        })
        #try:
        #    r = viewfunc(*args, **kwargs)
        #    return r or ''
        #except Exception as e:
        #    traceback.print_exc()
        #    raise e
    return decorated_viewfunc


@app.route('/')
@app.route('/<path:path>')
@handle_exceptions
def get_path(path=''):
    """
    1. Download file

        GET /img/girl.jpg

    2. List directory

        GET /img

    3. Retrieve file/directory metadata

        GET /img?meta=true
        GET /img/girl.jpg?meta=true
        {
            "custom": {
                "transfer": {
                    "progress": {}
                }
            }
        }

    4. Query API page

        GET /?api=true
    """
    if 'api' in request.args:
        return render_template('api.html')

    visitor = get_visitor()
    node = get_existed_node(path)

    if 'meta' in request.args:
        return node.get_meta(visitor)
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

    2. Create directory

        PUT /img/

    3. Modify file/directory metadata

        PUT /img/girl.jpg
        {
            "meta": {
                "access": 0600
            }
        }
    """
    visitor = get_visitor()
    if path.endswith('/'):
        node = get_dir_node(path)
    else:
        node = get_file_node(path)
    if not node.exist:
        node.create(visitor)
    node.update_meta(visitor, get_request_meta())
    if request.files:
        pass  # TODO handle upload


@app.route('/<path:path>', methods=['POST'])
@handle_exceptions
def post_path(path):
    """
    1. Rename file/directory

        POST /img/girl.jpg
        {
            "op": "mv",
            "to": "t.jpeg"
        }

    2. Move file/directory

        POST /img/girl.jpg
        {
            "op": "mv",
            "to": "/public/girl.jpg"
        }

    3. Copy file/directory

        POST /img/girl.jpg
        {
            "op": "cp",
            "to": "/public/girl.jpg"
        }
    """
    src = get_existed_node(path)
    op = get_request_operation()
    visitor = get_visitor()
    if op == 'mv':
        dst = get_dst_node(node, request.args.get('to'))
        src.move(user, dst)
    elif op == 'cp':
        if not dst.clone(user, src):
            raise BadRequest


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
    return r


def get_visitor():
    try:
        token = request.headers['authorization'].split(' ')[1]
        user = jwt.decode(token, conf.auth_pubkey, algorithm='RS512')
        if not fsutil.get_home_dir(user).exist:
            fsutil.create_home_dir_for(user)
    except Exception:
        user = {'username': 'guest'}
    return User(user)


def get_request_meta():
    data = request.json or {}
    return data.get('meta')


def get_request_operation():
    op = request.args.get('op')
    if not op:
        raise BadRequest


def get_dst_node(src, to):
    if not to.startswith('/'):
        to = src.parent.path + '/' + to
    return get_node(to)


def uploading_file():
    return bool(request.files)


def make_content_stream(node):
    return Response(node.iter_data(), mimetype=node.mimetype)


BadRequest = 'Bad Request', 400
#Forbidden = error_response('Forbidden', 403)
#NotFound = error_response('Not Found', 404)


if __name__ == '__main__':
    if not fsutil.initialized():
        fsutil.create_root_dir()
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=True)
