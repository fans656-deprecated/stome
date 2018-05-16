import os
import json

from flask import *

import conf
import util
import filesystem


app = Flask(__name__, template_folder='.')


@app.route('/')
@app.route('/<path:path>')
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
    if requesting_api():
        return render_template('api.html')

    node = get_node(path)
    if not node.exist:
        return NotFound

    visitor = get_visitor()
    if requesting_meta():
        if node.readable_by(visitor):
            return ok_response(node.meta)
        else:
            return Forbidden
    elif node.isdir:
        if node.readable_by(visitor) and node.executable_by(visitor):
            return ok_response(list_directory(node))
        else:
            return Forbidden
    else:  # is file
        if node.readable_by(visitor):
            return make_content_stream(node)
        else:
            return Forbidden


@app.route('/<path:path>', methods=['PUT'])
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
    node = get_node(path)
    if not node.exist:
        if not node.creatable_by(visitor):
            return Forbidden
        if requesting_directory(path):
            node.type = 'dir'
        node.create(owner=visitor)
    meta = get_request_meta()
    if meta:
        if not node.own_by(visitor):
            return Forbidden
        node.update_meta(meta)
    if uploading_file():
        if not node.writable_by(visitor):
            return Forbidden
        try:
            data_meta = get_uploading_meta()
            data_file = get_uploading_data_file()
            node.write(meta=data_meta, data=data_file)
        except Exception:
            return BadRequest
    return ok_response()


@app.route('/<path:path>', methods=['POST'])
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
    node = get_node(path)
    if not node.exist:
        return NotFound
    operation = get_request_operation()
    if not operation:
        return BadRequest
    visitor = get_visitor()
    if operation == 'mv':
        dst_path = get_request_dst_path()
        if not dst_path:
            return BadRequest
        dst_node = get_node(dst_path, parent=node.parent.path)
        try:
            cp(node, dst_node, visitor)
            return OK()
        except PermissionDenied as e:
            return Forbidden()


@app.route('/<path:path>', methods=['DELETE'])
def delete_path(path):
    """
    Delete file/directory

        DELETE /img
        DELETE /img/girl.jpg
    """
    pass


@app.after_request
def after_request(r):
    r.headers['Cache-Control'] = 'no-cache'
    return r


def get_node(path, parent='/'):
    if not path.startswith('/'):
        path = os.path.join(parent, path)
    path = normalized_path(path)
    node = filesystem.get_node_by_path(path)
    return node


def get_visitor():
    try:
        token = request.headers['authorization'].split(' ')[1]
        user = jwt.decode(token, conf.auth_pubkey, algorithm='RS512')
    except Exception:
        user = {'username': ''}
    return User(user)


def get_request_meta():
    data = request.json or {}
    return data.get('meta')


def get_request_operation():
    return request.args.get('op')


def get_request_dst_path():
    return request.args.get('to', '')


def normalized_path(path):
    if not path.startswith('/'):
        path = '/' + path
    return path


def requesting_api():
    return 'api' in request.args


def requesting_directory(path):
    return path.endswith('/')


def requesting_meta():
    return 'meta' in request.args


def uploading_file():
    return bool(request.files)


def list_directory(directory):
    subdirs = directory.subdirs
    files = directory.files
    return {
        'dirs': map(make_list_directory_entry, subdirs),
        'files': map(make_list_directory_entry, files),
    }


def make_list_directory_entry(node):
    return {
        'name': node.name,
        'path': node.path,
    }


def make_content_stream(node):
    return Response(node.iter_data(), mimetype=node.mimetype)


def cp(src, dst, visitor):
    if not dst.exist:
        if not dst.parent.writable_by(visitor):
            return Forbidden
        dst.create(owner=visitor)
    if not dst.own_by(visitor) and dst.writable_by(visitor):
        return Forbidden
    dst.replace_meta(src.meta)
    if not dst.removable_by(visitor):
        return Forbidden
    src.remove()
    src.save()
    dst.save()
    return ok_response()


def ok_response(data=None):
    if isinstance(data, (str, unicode)):
        data = {'detail': data}
    return json.dumps(data or {}), 200


def error_response(data=None, status_code=400):
    if isinstance(data, (str, unicode)):
        data = {'detail': data}
    return json.dumps(data or {}), status_code


OK = ok_response
BadRequest = error_response('Bad Request', 400)
Forbidden = error_response('Forbidden', 403)
NotFound = error_response('Not Found', 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=True)
