# yes

__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


import MySQLdb
import logging
from MySQLdb import Error as MySqlError

from cdsapi import cfg
from cdsapi.exc import NotFound


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class _MysqlBase(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(
                host=CONF.db.host,
                user=CONF.db.user,
                passwd=CONF.db.passwd,
                db=CONF.db.name,
                port=int(CONF.db.port))
            self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.conn = None
            LOG.error(str(e))

    def clear(self):
        self.cur.close()
        self.conn.close()

    def runCommand(self, cmd):
        try:
            if not self.conn or not self.cur:
                raise MySqlError('Not Connect DB')
            self.cur.execute(cmd)
            return self.cur.fetchall()
        except Exception, e:
            LOG.error(str(e))
            raise MySqlError(str(e))


class TasksTable(_MysqlBase):

    table = CONF.db.tasks

    def get(self, task_id):
        cmd = "select * from %s where task_id='%s'" % (self.table, task_id)
        LOG.debug('tasks GET command: %s ' % cmd)
        tasks = self.runCommand(cmd)
        if tasks:
            return tasks
        else:
            raise NotFound('not found task: %s' % task_id, '01202')


class InstancesTable(_MysqlBase):

    table = CONF.db.instances

    def list(self, customers):
        cmd = "select * from %s where customers='%s'" % (self.table, customers)
        LOG.debug('instances GET_ALL cmd: %s' % cmd)
        instances = self.runCommand(cmd)
        if not instances:
            raise NotFound('Not a instance in Cds', '00202')
        return instances

    def add(self, **kwargv):
        pass

    def update(self, **kwargv):
        pass

    def delete(self, instance_uuid):
        pass


class IpTable(_MysqlBase):

    table = CONF.db.iptable

    def get_all(self, customers):
        pass

    def get(self):
        raise NotImplementedError('IpTable get interface Not Implemented')

    def add(self, **kwargv):
        pass

    def update(self, **kwargv):
        pass

    def delete(self, ipaddress):
        pass


class TemplateTable(_MysqlBase):
    table = CONF.db.template

    def get_all(self):
        raise NotImplementedError('Template get interface Not Implemented')

    def get(self, name):
        pass

    def add(self, **kwargv):
        pass

    def delete(self, name):
        raise NotImplementedError('TemplateTable delete interface Not Implemented')


class DriversTable(_MysqlBase):

    table = CONF.db.driver

    def get_all(self):
        raise NotImplementedError('Drivers get interface Not Implemented')

    def update_drivers(self, status):
        raise NotImplementedError('Drivers update interface Not Implemented')
