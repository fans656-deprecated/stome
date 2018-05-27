import pymongo


g_db = None


def getdb():
    global g_db
    if g_db is None:
        g_db = newdb()
    return g_db


def newdb():
    return pymongo.MongoClient().stome

if __name__ == '__main__':
    db = getdb()
    r = db.content.find()
    print '=' * 40, 'content'
    for x in r:
        print x
    print '=' * 40, 'instance'
    r = db.instance.find()
    for x in r:
        print x
