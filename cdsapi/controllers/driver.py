
__author__ = 'hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'

import logging
import simplejson as json
# import pecan
from pecan import rest
# from pecan import abort
from pecan import expose
import wsmeext.pecan as wsme_pecan

from cdsapi.model import Driver


LOG = logging.getLogger(__name__)


class DriverController(rest.RestController):

    @wsme_pecan.wsexpose(Driver)
    def get_all(self):
        driver = Driver()
        driver.name = 'openstack'
        driver.status = True
        return Driver.from_db_model(driver)
