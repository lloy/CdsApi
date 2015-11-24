
__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


import logging
import uuid
import time
import datetime
import wsmeext.pecan as wsme_pecan
from pecan import rest
from pecan import request
from wsme import types as wtypes
from MySQLdb import Error as MySqlError

from cdsapi.model import Instances
from cdsapi.model import TaskUuid
from cdsapi.model import Query
from cdsapi import exc


LOG = logging.getLogger(__name__)
IPFLAG_STATUS = ('ALL', 'ALLOC', 'UN_ALLOC')
TASKS_STATUS = ('OK', 'PROCESSING', 'ERROR')


class InstancesController(rest.RestController):

    def _query_to_kwargs(self, query):
        kw = {}
        for q in query:
            if q.op == 'eq':
                if q.field == 'model_type':
                    kw['instance_type'] = q.value
                elif q.field == 'customers':
                    continue
                else:
                    kw[q.field] = q.value
            elif q.op == 'lt' or q.op == 'gt':
                # lt and gt options Not implementation
                pass
            elif q.op == 'le' or q.op == 'ge':
                # le and ge options Not implementation
                pass
        return kw

    @wsme_pecan.wsexpose([Instances], [Query])
    def get_all(self, q=None):

        query = q or []
        kwargs = self._query_to_kwargs(query)
        LOG.debug("INPUT ARGS :%s" % kwargs)
        instances = []
        for ins in request.instancehook.list('1hao', **kwargs):
            instances.append(Instances.from_db_model(ins))
        return instances

    @wsme_pecan.wsexpose(TaskUuid, wtypes.text, wtypes.text, int, wtypes.text)
    def post(self, model_type, template_type, instances_num, flag):
        # start_ipaddress = '20.1.10.1'
        """
        parms
            task_id: task uniquely identifies
            create_time: task create time
            template_type: instance template type
            model_type: instance type
            status: task status
            flag: fixable or unfixable
            instances_num: create instance number
        """
        LOG.debug('model_type: %s' % model_type)
        LOG.debug('template_type: %s' % template_type)
        LOG.debug('instances_num: %s' % instances_num)
        LOG.debug('flag: %s' % flag)
        if not request.templatehook.get(template_type):
            raise exc.NotSupportType('Not Support template %s' % template_type, '00002')

        task_id = str(uuid.uuid1())
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        kw = dict(task_id=task_id,
                  create_time=timestamp,
                  template_type=template_type,
                  model_type=model_type,
                  flag=flag,
                  status=TASKS_STATUS[1],
                  instances_num=instances_num
                  )
        try:
            request.taskhook.add(**kw)
        except MySqlError:
            LOG.error('insert task into mysql failed')
            raise

        return TaskUuid.from_model(task_id)

    @wsme_pecan.wsexpose(Instances, wtypes.text, status_code=204)
    def delete(self, instance_uuid):
        LOG.debug('instance_uuid %s' % instance_uuid)
        request.instancehook.delete(instance_uuid)
