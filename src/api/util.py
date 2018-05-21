import hashlib
import datetime


def calc_md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


def utc_now_str():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')


def normalized_path(path):
    if not path:
        return '/'
    if len(path) > 1 and path.endswith('/'):
        path = path[:-1]
    parts = []
    for part in path.split('/'):
        if not part or part == '.':
            continue
        elif part == '..':
            if parts:
                parts.pop()
        else:
            parts.append(part)
    path = '/'.join(parts)
    if not path.startswith('/'):
        path = '/' + path
    return path
