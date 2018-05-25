import pymongo


def getdb(g={}):
    """
    stome.node - node
    stome.file - store
    stome.storage - store
    """
    if 'db' not in g:
        g['db'] = pymongo.MongoClient().stome
    return g['db']


if __name__ == '__main__':
    db = getdb()
    print db.collection_names()
    #print next(db.node.find({}))
    #print next(db.file.find({}))
    print next(db.content.find({}))
