# yes

__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


import pecan
import simplejson as json
import six


class ClientSideError(RuntimeError):
    def __init__(self, msg=None, status_code=400):
        self.msg = msg
        self.code = status_code
        super(ClientSideError, self).__init__(self.faultstring)

    @property
    def faultstring(self):
        if self.msg is None:
            return str(self)
        elif isinstance(self.msg, six.text_type):
            return self.msg
        else:
            return six.u(self.msg)

    # def __str__(self):
        # return 'faultcode=%s, faultstring=%s, debuginfo=%s' % (
            # self.faultcode, self.faultstring, self.debuginfo
        # )


class ApiBaseError(ClientSideError):

    def __init__(self, error, faultcode=00000, status_code=400):
        self.faultcode = faultcode
        kw = dict(msg=unicode(error), faultcode=faultcode)
        self.error = json.dumps(kw)
        pecan.response.translatable_error = error
        super(ApiBaseError, self).__init__(self.error, status_code)


class NotFound(ApiBaseError):
    def __init__(self, error, faultcode):
        super(NotFound, self).__init__(error, faultcode, status_code=404)


class NotSupportType(ApiBaseError):
    def __init__(self, error, faultcode):
        super(NotSupportType, self).__init__(error, faultcode, status_code=501)


class BaseError(Exception):

    def __init__(self, message, errno='0000-000-00'):
        self.msg = message
        self.code = errno
        super(BaseError, self).__init__(self.msg, self.code)


class ConfigureException(BaseError):

    """
    errno = 0000-001-00
    """

    def __init__(self, message, errno='0000-001-00'):
        super(ConfigureException, self).__init__(message, errno)


class NotSetPoller(ConfigureException):
    """
    errno = 0000-001-02
    """
    pass


class SetPollerError(Exception):
    pass


class NotRunMethod(BaseError):
    """
    errno = 0000-003-01
    """
    pass


class NotFoundConfigureFile(Exception):
    pass


class TaskNotFound(Exception):
    pass
