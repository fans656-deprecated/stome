import json

from flask import *
import requests

import conf


app = Flask(__name__, template_folder='.')


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    r.headers['Cache-Control'] = 'public, max-age=0'
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_file(path):
    if request.args.get('static'):
        return send_from_directory('.', path)
    r = requests.get(conf.server_origin + '/' + path + '?isdir=true')
    r = json.loads(r.text)
    if r['isdir']:
        return send_from_directory('.', 'index.html')
    else:
        r = requests.get(conf.server_origin + '/' + path, stream=True)
        return Response(r.iter_content(1024 * 1024), mimetype=r.headers['content-type'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=True)
