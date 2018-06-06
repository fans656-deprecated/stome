import pymongo


g_db = None


def getdb():
    global g_db
    if g_db is None:
        g_db = newdb()
    return g_db


def newdb():
    return pymongo.MongoClient().stome


def use_new():
    global g_db
    g_db = newdb()


if __name__ == '__main__':
    from tests.prepare import *

    db = getdb()

    #for c in db.list_collections():
    #    print c
    #exit()

    print '=' * 40, 'dir node'
    r = db.node.find({'type': 'dir'})
    for x in r:
        print_node_meta(x)

    print '=' * 40, 'file node'
    r = db.node.find({'type': 'file'})
    for x in r:
        print x

    #print '=' * 40, 'content'
    #r = db.content.find()
    #for x in r:
    #    print x
