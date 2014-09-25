
__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'

import logging
import pecan
from pecan import rest
# from pecan import abort
# from pecan import expose
import wsmeext.pecan as wsme_pecan

from cdsapi.model import Instances


LOG = logging.getLogger(__name__)


class InstancesController(rest.RestController):

    @wsme_pecan.wsexpose(Instances, unicode)
    def get_all(self):

        return dict(status='OK')
        # return map(Instances.from_db_model,
                   # pecan.request.storage_conn.get_drivers)
