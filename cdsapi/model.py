# yes

import inspect
import wsme
import datetime
from wsme import types as wtypes

__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


class _Base(wtypes.Base):

    @classmethod
    def from_db_model(cls, m):
        return cls(**(m.as_dict()))

    def as_dict(self, db_model):
        valid_keys = inspect.getargspec(db_model.__init__)[0]
        if 'self' in valid_keys:
            valid_keys.remove('self')
        return self.as_dict_from_keys(valid_keys)

    def as_dict_from_keys(self, keys):
        return dict((k, getattr(self, k))
                    for k in keys
                    if hasattr(self, k) and
                    getattr(self, k) != wsme.Unset)


class Driver(_Base):

    name = wtypes.text
    status = wsme.wsattr(bool, default=True)

    @classmethod
    def from_db_model(cls, m):
        return cls(
            name=m.name,
            status=m.status)


class Instances(_Base):
    instance_uuid = wtypes.text
    name = wtypes.text
    ip = wtypes.text
    status = wtypes.text
    # across api set action in [add, delete]
    # across agent set action value in [None, delete, deleting]
    source = wtypes.text  # suporrt only two kinds of iaas, [vsphere, openstack]


class Tasks(_Base):
    Tasks_id = wtypes.text  # task id
    createtime = datetime.datetime  # create time
    status = wtypes.text  # task status [OK, PROCESSING, ERROR]
    instances_num = int  # in this task has instances_num instances
    template_type = wtypes.text  # Instances template type , eg: large, tiny, small
    completed_num = int  # in processing already completed instances number
    completed_instances = list()  # already completed instances detail
