import subprocess

import jwt

import conf
import db


def execute(d):
    cmd = build_cmd(d)
    return subprocess.check_output(cmd, shell=True)


def build_auth_header(user):
    token = {'user': user}
    encoded_token = jwt.encode({'user': user}, auth_pri_key, 'RS512')
    return 'Authorization: Bearer {}'.format(encoded_token)


def build_cmd(d):
    url = '{}{}'.format(origin, d['path'])
    args = {}
    if d.get('isdir'):
        args['isdir'] = 'true'
    if d.get('owner'):
        args['owner'] = d['owner']
    url += '?' + '&'.join('{}={}'.format(k, v) for k, v in args.items())
    cmd = 'curl -s -X{method} {url}'.format(
        method=d['method'],
        url=url,
    )
    if d.get('visitor'):
        cmd += ' -H "{}"'.format(build_auth_header(d['visitor']))
    if d.get('file'):
        cmd += ' -F data=@{}'.format(d['file'])
    return cmd


def test_create_directory():
    paths = ['', '/img', '/img/girl/tmp']
    for owner in users:
        for visitor in users:
            for path in paths:
                create_directory(owner, visitor, path)
                create_directory(owner, visitor, path + '/')


def create_directory(owner, visitor, path):
    r = execute({
        'owner': owner,
        'visitor': visitor,
        'path': path,
        'method': 'PUT',
        'isdir': True,
    })
    if not path or path == '/':
        assert '405' in r
    elif get_owner(owner) != visitor:
        assert '401' in r
    elif get_owner(owner) == visitor:
        assert '0' in r
    else:
        print owner, visitor, path
        print r
        exit()
    return r


def upload_file(owner, visitor, path, local_path):
    return execute({
        'owner': owner,
        'visitor': visitor,
        'path': path,
        'method': 'PUT',
        'file': local_path,
    })


def get_owner(owner):
    return owner or conf.default_owner


users = [None, 'fans656', 'twiispa', 'no-one', r'/!\?']
auth_pri_key = open('/home/fans656/.ssh/id_rsa').read().strip()
origin = 'http://localhost:{}'.format(conf.port)

db.init_db()
#print create_directory(None, 'fans656', '/foo/bar')
print create_directory(None, 'fans656', '/img/girl')
#print upload_file(None, 'fans656', '/test.txt', 'test.py')
#print upload_file(None, 'fans656', '/img/girl/blue.jpg', 'test.py')
#print execute({
#    'method': 'GET',
#    'path': '/foo/bar'
#})
