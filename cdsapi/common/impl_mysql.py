# yes

import MySQLdb
import logging
from MySQLdb import Error as MySqlError

from cdsapi import cfg


__author__ = 'Hardy.zheng'

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class MysqlBase(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(
                host=CONF.db.host,
                user=CONF.db.user,
                passwd=CONF.db.passwd,
                db=CONF.db.name,
                port=int(CONF.db.port))
            self.cur = self.conn.cursor
        except MySQLdb.Error, e:
            self.conn = None
            LOG.error(str(e))

    def clear(self):
        self.cur.close()
        self.conn.close()


class DriversDb(MysqlBase):

    def __init__(self):
        self.table = CONF.db.driver
        # super(DriversDb, self).__init__()

    def get_drivers(self):
        return dict(name='openstack', status=True)

        # cmd = 'select * from %s' % self.table
        # try:
            # if not self.conn or not self.cur:
                # raise MySqlError('Not Connect DB')
            # self.cur.execute(cmd)
            # results = self.cur.fetchall()
            # self.conn.close()
            # return results
        # except Exception, e:
            # LOG.error(str(e))
            # raise MySqlError(str(e))

    def update_drivers(self, status):
        return dict(status='OK')
        # try:
            # cmd = 'update %s set status=%d' % (self.table, status)
            # self.cur.execute(cmd)
            # self.conn.commit()
        # except Exception, e:
            # LOG.DEBUG('run Command: %s' % cmd)
            # LOG.ERROR('DriversDb.update_drivers not successful')
            # raise MySqlError(str(e))


class IaasDb(MysqlBase):
    def __init__(self):
        self.table = CONF.db.iaas
        super(IaasDb, self).__init__()

    def get_instances(self):
        return list('123')
