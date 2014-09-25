# yes
from pecan import hooks

from cdsapi.common.impl_mysql import DriversDb


__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


class DBHook(hooks.PecanHook):

    def __init__(self):
        self.storage_connection = DriversDb()

    def before(self, state):
        state.request.storage_conn = self.storage_connection


class APIHook(hooks.PecanHook):

    def __init__(self):
        raise NotImplementedError('API Not Implemented')

    def before(self, state):
        raise NotImplementedError('API Not Implemented')
