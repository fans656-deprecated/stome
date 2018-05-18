import json

from flask import *
import requests

import conf


app = Flask(__name__)


@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache'
    return r


@app.route('/')
@app.route('/<path:path>')
def index(path=''):
    if 'static' in request.args:
        return send_from_directory('.', path)
    return send_from_directory('.', 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=conf.port, threaded=True, debug=True)
