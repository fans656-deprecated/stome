class BadWrite(Exception):

    def __init__(self, path, meta):
        self.path = path
        self.meta = meta


class OperationError(Exception):

    def __init__(self, path):
        self.path = path


class NotExist(OperationError): pass
class NotDir(OperationError): pass
class DirExisted(OperationError): pass
class CantRead(OperationError): pass
class CantWrite(OperationError): pass
class CantCreate(OperationError): pass
class CantRemove(OperationError): pass
