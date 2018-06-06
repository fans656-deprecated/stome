import test_fsutil
from tests.prepare import *
from filesystem import get_node


def run():
    existance_test()


def existance_test():
    # 1. non-existed resource
    for path in [
            '/asdf',
            '/asdf/asdf',
            '/asdf/asdf/asdf',
    ]:
        assert not get_node(root_user, path).exists
        assert not get_node(normal_user, path).exists
        assert not get_node(guest_user, path).exists

    # 2. existed resource
    init()

    # 2.1 non-readable

    # 2.2 readable
