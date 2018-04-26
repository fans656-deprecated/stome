import sys; sys.path.append('..')
import os
import traceback

from flask import *
import jwt

import conf
import util
import errors


app = Flask(__name__, template_folder='.')


@app.route('/')
def index():
    if 'api' in request.args:
        return render_template('api.html', origin=request.host_url[:-1])
    if not authorized():
        return errors.Unauthorized
    return errors.NotFound


@app.route('/<md5>', methods=['GET', 'PUT'])
def upload(md5):
    #if not authorized():
    #    return errors.Unauthorized
    try:
        if request.method == 'GET':
            fpath = os.path.join(conf.files_dir, md5)
            if not os.path.exists(fpath):
                return errors.NotFound
            return Response(chunked_file(fpath))
        else:
            data = request.files.get('data').read()
            if is_upload_parts():
                pos = int(request.form.get('pos'))
                part_size = int(request.form.get('part-size'))
                save_file(md5, data, pos, part_size)
                return errors.OK
            else:
                assert md5 == util.calc_md5(data)
                save_file(md5, data)
                return errors.OK
    except Exception as e:
        traceback.print_exc(e)
        return errors.BadRequest


def authorized():
    try:
        encoded_token = request.headers.get('authorization').split()[1]
        decoded_unverified_token = jwt.decode(encoded_token, verify=False)
        pubkey = decoded_unverified_token['pubkey']
        assert pubkey in conf.pubkeys
        jwt.decode(encoded_token, pubkey, 'RS512')
        return True
    except Exception:
        return False


def save_file(name, data, pos=0, part_size=None):
    if not os.path.exists(conf.files_dir):
        os.makedirs(conf.files_dir)
    fpath = os.path.join(conf.files_dir, name)
    if not os.path.exists(fpath):
        open(fpath, 'wb').close()
    with open(fpath, 'rb+') as f:
        f.seek(pos, os.SEEK_SET)
        f.write(data)


def is_upload_parts():
    return 'pos' in request.form


def chunked_file(fpath):
    with open(fpath, 'rb') as f:
        while True:
            data = f.read(1024 * 1024)
            if not data:
                break
            yield data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, threaded=True, debug=True)
