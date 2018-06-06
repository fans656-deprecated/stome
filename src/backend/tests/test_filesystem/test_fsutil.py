from filesystem.fsutil import *


def run():
    erase_everything()
    assert not initialized()
    create_root_dir()
    assert initialized()
