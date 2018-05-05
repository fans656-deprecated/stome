import sys; sys.path.append('..')
import json
import traceback
import hashlib

import jwt
from flask import *

import db
import util
import conf
import resource


app = Flask(__name__, template_folder='.')


OK = json.dumps({'errno': 0, 'info': 'OK'})
BadRequest = json.dumps({'errno': 400, 'info': 'Bad Request'}), 400
Unauthorized = json.dumps({'errno': 401, 'info': 'Unauthorized'}), 401
NotFound = json.dumps({'errno': 404, 'info': 'Not Found'}), 404
Conflict = json.dumps({'errno': 409, 'info': 'Conflict'}), 409


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = '*'
    return r


@app.teardown_appcontext
def close_connection(exc):
    db.close_db()


@app.route('/')
def index():
    if request.args:
        if 'api' in request.args:
            return render_template('api.html', origin=request.host_url)
        elif 'test' in request.args:
            return render_template('test.html', origin=request.host_url)
    if not accessible('', mode='r'):
        return Unauthorized
    return handle_list_directory('')


@app.route('/<path:path>', methods=['GET'])
def get_resource(path):
    #if not accessible(path, mode='r'):
    #    return Unauthorized
    r = resource.load(get_owner(), path)
    if 'isdir' in request.args:
        return json.dumps({'isdir': r.isdir})
    elif 'info' in request.args:
        return json.dumps({
            'path': path,
            'isdir': r.isdir,
            'md5': r.md5,
        })
    else:
        if r.isdir:
            return handle_list_directory(path)
        else:
            chunked_data_iter, mimetype = handle_download_file(path)
            return Response(chunked_data_iter, mimetype=mimetype)


@app.route('/<path:path>', methods=['OPTIONS', 'PUT'])
def put_resource(path):
    if request.method == 'OPTIONS':
        return ''
    if not accessible(path, mode='w'):
        return Unauthorized
    try:
        if is_create_directory():
            handle_create_directory(path)
        elif is_upload_file():
            handle_upload_file(path)
        elif is_change_access():
            handle_change_access(path)
        else:
            return BadRequest
        return OK
    except Exception as e:
        traceback.print_exc(e)
        return BadRequest


def accessible(path, mode):
    owner = get_owner()
    visitor = get_visitor()
    return resource.load(owner, path).accessible_by(visitor, mode)


def get_owner():
    return request.args.get('owner') or conf.default_owner


def get_visitor():
    encoded_token = get_encoded_auth_token()
    if not encoded_token:
        return None
    decoded_token = jwt.decode(encoded_token, conf.pubkey, 'RS512')
    return decoded_token['user']


def get_encoded_auth_token():
    auth_header_value = request.headers.get('authorization')
    if not auth_header_value:
        return None
    return auth_header_value.split()[1]


def is_create_directory():
    return 'isdir' in request.args


def is_upload_file():
    return 'data' in request.files


def is_change_access():
    return 'group' in request.form or 'permission' in request.form


def is_upload_as_parts():
    return 'pos' in request.form


def handle_list_directory(path):
    content_list = resource.load(get_owner(), path).list()
    content_list.update({'errno': 0})
    return json.dumps(content_list)


def handle_download_file(path):
    r = resource.load(get_owner(), path)
    chunked_data_iter = r.chunked_load()
    return chunked_data_iter, r.mimetype


def handle_create_directory(path):
    owner = get_owner()
    group, permission = get_group_and_permission()
    resource.new(owner, path, group, permission, isdir=True).serialize()


def handle_upload_file(path):
    data = request.files.get('data').read()
    group, permission = get_group_and_permission()
    owner = get_owner()
    if is_upload_as_parts():
        md5 = request.form.get('md5')
        pos = request.form.get('pos')
        part_size = request.form.get('part-size')
        mimetype = request.form.get('mimetype')
        pos = int(pos)
        part_size = int(part_size)
        r = resource.new(owner, path, group, permission,
                         md5=md5,
                         mimetype=mimetype)
        r.save(data, pos, part_size)
        r.serialize()
    else:
        r = resource.new(owner, path, group, permission,
                         md5=util.calc_md5(data),
                         mimetype=request.form.get('mimetype'))
        r.save(data)
        r.serialize()


def handle_change_access(path):
    pass


def get_group_and_permission():
    group = request.form.get('group') or ''
    permission = str(request.form.get('permission') or conf.default_permission)
    return group, permission


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=True)
