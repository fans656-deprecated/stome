import os
import json
from pprint import pprint
from collections import OrderedDict

import requests
import jwt

import conf
import util
from db import getdb
from node import get_node
from test.setup import *
from store import *
import store


print store.storage.get_templates()


def upload_file():
    class Stream(object):

        def __init__(self, s):
            self.s = s
            self.i = 0

        def read(self, n):
            i = self.i
            r = self.s[i:i+n]
            self.i = i + n
            return r

    getdb().content.remove()

    id = 'foo'
    data = 'hello world you'
    md5 = util.calc_md5(data)
    print md5

    content = get_content(id)

    content.create(len(data))
    print content

    content.write(Stream(data), 0, md5)
    print content
