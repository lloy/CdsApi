
__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'


import logging
import wsmeext.pecan as wsme_pecan
from pecan import rest
from pecan import request

from cdsapi.model import Instances


LOG = logging.getLogger(__name__)


class InstancesController(rest.RestController):

    @wsme_pecan.wsexpose(Instances)
    def get_all(self):
        instances = request.instancehook.list('1hao')
        print instances
