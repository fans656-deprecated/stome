class Error(Exception):

    def __init__(self, detail, errno=400):
        if isinstance(detail, dict):
            self.result = detail
        elif isinstance(detail, (str, unicode)):
            self.result = {'detail': detail}
        self.errno = errno


class PermissionDenied(Error):

    def __init__(self, path):
        super(PermissionDenied, self).__init__(path + ' permission denied', 401)
