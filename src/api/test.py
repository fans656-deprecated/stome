import tests

from tests.prepare import *


#tests.test_filesystem.run()
#testsitest_filesystemitest_fsutil.run()


init()

r = requests.post(origin + '/foo?op=mkdir')
print r
print r.text

#from filesystem.fsutil import *
#node = get_node(root_user, '/public')
#node.create_as_dir()
