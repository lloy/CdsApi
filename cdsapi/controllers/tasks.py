# yes

__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


import logging
import wsmeext.pecan as wsme_pecan
from wsme import types as wtypes
from pecan import rest
from pecan import request

from cdsapi.model import Tasks
from cdsapi.model import Instances


LOG = logging.getLogger(__name__)


class TasksController(rest.RestController):

    @wsme_pecan.wsexpose(Tasks, wtypes.text)
    def get_one(self, task_id):
        LOG.debug('input argv %s' % task_id)
        ins_pool = list()
        instance = dict(
            instance_uuid='1111',
            name='instance01',
            ip='192.188.8.10',
            # across api set action in [add, delete]
            status='running',
            # across agent set action value in [None, delete, deleting]
            template_type='ubuntu12.01',
            os_type='ubuntu12',
            username='test',
            passwd='12345',
            # time='online_time',  # online_time, off_time, create_time
            # suporrt only two kinds of iaas, [vsphere, openstack]
            iaas_type='openstack',
            customers='1hao')
        ins = Instances(**instance)
        t = request.taskhook.get(task_id)
        LOG.debug('Found task: %s' % t)
        ins_pool.append(ins)
        task = Tasks.from_db_model(t[0], len(ins_pool), ins_pool)
        return task
