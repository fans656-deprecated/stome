class OperationError(Exception):

    def __init__(self, path, errno=400):
        self.path = path
        self.errno = errno

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.path)


class NotExist(OperationError): pass
class NotDir(OperationError): pass
class DirExisted(OperationError): pass
class CantRead(OperationError): pass
class CantWrite(OperationError): pass
class CantCreate(OperationError): pass
class CantRemove(OperationError): pass
