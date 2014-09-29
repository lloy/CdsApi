# yes

__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


class ApiBase(Exception):

    def __init__(self, message, errno='0000-000-00'):
        self.msg = message
        self.code = errno
        super(ApiBase, self).__init__(self.msg, self.code)


class NotFound(ApiBase):
    pass


class ConfigureException(ApiBase):

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


class NotRunMethod(ApiBase):
    """
    errno = 0000-003-01
    """
    pass


class NotFoundConfigureFile(Exception):
    pass
