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
