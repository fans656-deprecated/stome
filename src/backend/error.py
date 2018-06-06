class Error(Exception):

    def __init__(self, result_or_detail, errno=400):
        if isinstance(result_or_detail, dict):
            self.result = result_or_detail
        elif isinstance(result_or_detail, (str, unicode)):
            self.result = {'reason': result_or_detail}
        self.result.update({
            'errno': errno,
        })
        self.errno = errno


class ResourceError(Error):

    def __init__(self, reason, resource, errno=400):
        result = {
            'reason': reason,
            'resource': resource,
        }
        super(ResourceError, self).__init__(result, errno)


class PermissionDenied(ResourceError):

    def __init__(self, resource):
        super(PermissionDenied, self).__init__(
            'Permission denied', resource, 401
        )


class NotFound(ResourceError):

    def __init__(self, resource):
        super(NotFound, self).__init__('Not found', resource, 404)


class Conflict(ResourceError):

    def __init__(self, resource):
        super(Conflict, self).__init__('Conflict', resource, 409)
