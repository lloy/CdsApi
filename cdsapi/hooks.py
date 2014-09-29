# yes

__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


from pecan import hooks

from cdsapi.common.impl_mysql import TasksTable
from cdsapi.common.impl_mysql import InstancesTable
from cdsapi.common.impl_mysql import IpTable


class InstancesHook(hooks.PecanHook):

    def __init__(self):
        self.storage_connection = InstancesTable()

    def before(self, state):
        state.request.instancehook = self.storage_connection


class TasksHook(hooks.PecanHook):

    def __init__(self):
        self.storage_connection = TasksTable()

    def before(self, state):
        state.request.taskhook = self.storage_connection


class IpTableHook(hooks.PecanHook):

    def __init__(self):
        self.storage_connection = IpTable()

    def before(self, state):
        state.request.iphook = self.storage_connection


class APIHook(hooks.PecanHook):

    def __init__(self):
        raise NotImplementedError('API Not Implemented')

    def before(self, state):
        raise NotImplementedError('API Not Implemented')
