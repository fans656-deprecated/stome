import json
import hashlib
import datetime

import jwt
from flask import request

import conf


def calc_md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


def success_response(data=None):
    if isinstance(data, (str, unicode)):
        data = {'detail': data}
    return json.dumps(data or {}), 200


def error_response(data=None, status_code=400):
    if isinstance(data, (str, unicode)):
        data = {'detail': data}
    return json.dumps(data or {}), status_code


def utc_now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
