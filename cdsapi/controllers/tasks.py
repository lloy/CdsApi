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
from cdsapi import exc


LOG = logging.getLogger(__name__)


class TasksController(rest.RestController):

    @wsme_pecan.wsexpose(Tasks, wtypes.text)
    def get_one(self, task_id):
        LOG.debug('input argv %s' % task_id)
        ins_pool = []
        instances = request.instancehook.getInstancesfromtask_id(task_id)
        LOG.debug('storage in mysql instances : %s' % str(instances))

        if instances:
            for ins in instances:
                LOG.debug("task completed instance :%s" % str(ins))
                instance = Instances.from_db_model(ins)
                ins_pool.append(instance)

        t = request.taskhook.get(task_id)
        LOG.debug('Found task: %s' % t)
        if t:
            task = Tasks.from_db_model(t[0], len(ins_pool), ins_pool)
            return task
        else:
            LOG.error("%s Not Found" % task_id)
            raise exc.NotFound("%s Not Found" % (task_id), '01202')
