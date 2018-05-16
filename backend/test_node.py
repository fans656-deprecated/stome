from node import *


# ------------------------------------------------------ normalized_path

assert normalized_path('') == '/'
assert normalized_path('/') == '/'
assert normalized_path('/foo') == '/foo'
assert normalized_path('/foo/') == '/foo'
assert normalized_path('foo/') == '/foo'
assert normalized_path('foo') == '/foo'
assert normalized_path('/..') == '/'
assert normalized_path('/../..') == '/'
assert normalized_path('/foo/bar/../') == '/foo'
exit()

# ------------------------------------------------------ parent

root = Node('/')
assert root.parent.path == '/'

node = Node('/foo')
assert node.parent.path == '/'

node = Node('/foo/')
assert node.parent.path == '/'

node = Node('/foo/bar')
assert node.parent.path == '/foo'

# ------------------------------------------------------ access

user_root = {'username': 'root'}
user_owner = {'username': 'foo'}
user_group = {'username': 'bar', 'groups': ['foo']}
user_other = {'username': 'baz'}

root = Node('/')
home = Node('/home/' + user_owner['username'])

assert root.readable_by(user_root)
assert root.writable_by(user_root)
assert homby(user_root)
assert home.writable_by(user_root)

assert home.readable_by(user_owner)
assert home.writable_by(user_owner)

assert home.readable_by(user_group)
assert home.writable_by(user_group)

assert home.readable_by(user_other)
assert not home.writable_by(user_other)
