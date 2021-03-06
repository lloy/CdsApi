
__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'

import logging
from pecan import rest
import wsmeext.pecan as wsme_pecan
from wsme import types as wtypes

from cdsapi.model import IpTable


LOG = logging.getLogger(__name__)


class IpTableController(rest.RestController):

    @wsme_pecan.wsexpose(IpTable, wtypes.text)
    def get_all(self, ipaddress):
        LOG.debug('input argv %s' % ipaddress)
