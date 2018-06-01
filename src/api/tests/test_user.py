import json
from pprint import pprint

from test.setup import *


"""
parent owner --
    owner cant create child
    owner cant remove child
child owner --
    owner cant read child
    owner cant write child
"""


def test_user(user, root, home, group_home, other_home, public):
    assert not user.own(root)
    assert not user.can_create(root)
    assert user.can_read(root)
    assert not user.can_write(root)
    assert not user.can_remove(root)

    for sub in get_subs(root):
        assert not user.own(sub)
        assert not user.can_create(sub)
        assert user.can_read(sub)
        assert not user.can_write(sub)
        assert not user.can_remove(sub)

    assert user.own(home)
    assert not user.can_create(home)
    assert user.can_read(home)
    assert user.can_write(home)
    assert not user.can_remove(home)

    assert user.own(home_sub)
    assert user.can_create(home_sub)
    assert user.can_read(home_sub)
    assert user.can_write(home_sub)
    assert user.can_remove(home_sub)

    assert not user.own(other_home)
    assert not user.can_create(other_home)
    assert user.can_read(other_home)
    assert user.can_write(other_home)
    assert not user.can_remove(other_home)

    assert user.own(home_sub)
    assert user.can_create(home_sub)
    assert user.can_read(home_sub)
    assert user.can_write(home_sub)
    assert user.can_remove(home_sub)


def get_subs(node):
    return [
        get_node(node.path + '/foo'),
        get_node(node.path + '/foo/bar'),
    ]


format_filesystem()
init_filesystem()


# user root
for d in [root_dir, home1, home2, public_dir]:
    assert user_root.own(d)
    assert user_root.can_create(d)
    assert user_root.can_read(d)
    assert user_root.can_write(d)
    assert user_root.can_remove(d)

test_user(user1, root_dir, home1, home1_sub, home2, home2_sub, public_dir)
